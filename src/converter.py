"""
converter.py - libvisio-ng を使った VSD/VSDX → SVG 変換モジュール
"""
from __future__ import annotations

import os
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


@dataclass
class ConversionResult:
    """変換結果を保持するデータクラス"""
    pages: list[bytes] = field(default_factory=list)   # SVGバイト列のリスト（ページ順）
    page_names: list[str] = field(default_factory=list)  # ページ名のリスト
    error: str | None = None

    @property
    def page_count(self) -> int:
        return len(self.pages)

    @property
    def success(self) -> bool:
        return self.error is None and len(self.pages) > 0


def convert_visio(
    file_path: str | Path,
    progress_callback: Callable[[int, int], None] | None = None,
) -> ConversionResult:
    """
    VSD または VSDX ファイルを SVG のリストに変換する。

    Args:
        file_path: 変換対象のファイルパス (.vsd or .vsdx)
        progress_callback: (current_page, total_pages) を受け取るコールバック

    Returns:
        ConversionResult: 変換結果（SVGバイト列のリスト + ページ名）
    """
    file_path = Path(file_path)

    if not file_path.exists():
        return ConversionResult(error=f"ファイルが見つかりません: {file_path}")

    suffix = file_path.suffix.lower()
    if suffix not in (".vsd", ".vsdx"):
        return ConversionResult(error=f"非対応のファイル形式です: {suffix}")

    try:
        import libvisio_ng  # noqa: F401
    except ImportError:
        return ConversionResult(
            error="libvisio-ng がインストールされていません。\n"
                  "pip install libvisio-ng を実行してください。"
        )

    try:
        return _do_convert(file_path, progress_callback)
    except Exception as e:
        return ConversionResult(error=f"変換中にエラーが発生しました:\n{e}")


def _do_convert(
    file_path: Path,
    progress_callback: Callable[[int, int], None] | None,
) -> ConversionResult:
    """実際の変換処理"""
    import libvisio_ng

    with tempfile.TemporaryDirectory(prefix="visio_viewer_") as tmp_dir:
        tmp_path = Path(tmp_dir)

        # libvisio-ng で変換（output_dirにSVGファイルが生成される）
        libvisio_ng.convert(str(file_path), output_dir=str(tmp_path))

        # 生成されたSVGファイルを収集（ページ順にソート）
        svg_files = sorted(tmp_path.glob("*.svg"), key=_page_sort_key)

        if not svg_files:
            return ConversionResult(error="SVGの生成に失敗しました（出力ファイルがありません）")

        total = len(svg_files)
        pages: list[bytes] = []
        page_names: list[str] = []

        for i, svg_file in enumerate(svg_files):
            if progress_callback:
                progress_callback(i + 1, total)

            svg_bytes = svg_file.read_bytes()
            pages.append(svg_bytes)
            page_names.append(_make_page_name(svg_file, i))

        return ConversionResult(pages=pages, page_names=page_names)


def _page_sort_key(path: Path) -> tuple[int, str]:
    """ファイル名に含まれる数字でソートするキー関数"""
    name = path.stem
    digits = "".join(c for c in name if c.isdigit())
    return (int(digits) if digits else 0, name)


def _make_page_name(svg_file: Path, index: int) -> str:
    """SVGファイル名からページ名を生成する"""
    stem = svg_file.stem
    # "page1", "Page-1" などの形式から番号を除いて名前を整形
    clean = stem.replace("-", " ").replace("_", " ").strip()
    return clean if clean else f"ページ {index + 1}"


def get_page_names_from_vsdx(file_path: str | Path) -> list[str]:
    """
    VSDX ファイルから変換せずにページ名だけを取得する（プレビュー用）。
    VSD ファイルには非対応（空リストを返す）。
    """
    file_path = Path(file_path)
    if file_path.suffix.lower() != ".vsdx":
        return []

    try:
        import xml.etree.ElementTree as ET

        with zipfile.ZipFile(file_path) as z:
            # visio/pages/pages.xml からページ名を読む
            with z.open("visio/pages/pages.xml") as f:
                tree = ET.parse(f)
                root = tree.getroot()

            ns = {"v": "http://schemas.microsoft.com/office/visio/2012/main"}
            names: list[str] = []
            for page in root.findall(".//v:Page", ns):
                name = page.get("Name", "")
                names.append(name if name else f"ページ {len(names) + 1}")
            return names
    except Exception:
        return []
