"""
converter.py - libvisio-ng を使った VSD/VSDX → SVG 変換モジュール
"""
from __future__ import annotations

import sys
import tempfile
import traceback
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from logger import log


@dataclass
class ConversionResult:
    """変換結果を保持するデータクラス"""
    pages: list[bytes] = field(default_factory=list)
    page_names: list[str] = field(default_factory=list)
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
    file_path = Path(file_path)
    log.info(f"convert_visio called: {file_path}")

    if not file_path.exists():
        msg = f"ファイルが見つかりません: {file_path}"
        log.error(msg)
        return ConversionResult(error=msg)

    suffix = file_path.suffix.lower()
    if suffix not in (".vsd", ".vsdx"):
        msg = f"非対応のファイル形式です: {suffix}"
        log.error(msg)
        return ConversionResult(error=msg)

    try:
        import libvisio_ng
        log.info(f"libvisio_ng imported OK: {libvisio_ng.__version__}")
    except ImportError as e:
        paths = "\n".join(sys.path[:8])
        msg = (f"libvisio_ng のインポートに失敗しました。\n\n"
               f"エラー詳細: {e}\n\n"
               f"sys.path (先頭8件):\n{paths}")
        log.error(msg)
        return ConversionResult(error=msg)

    try:
        return _do_convert(file_path, progress_callback)
    except Exception as e:
        tb = traceback.format_exc()
        log.error(f"変換中に例外:\n{tb}")
        return ConversionResult(error=f"変換中にエラーが発生しました:\n{e}\n\n{tb}")


def _do_convert(
    file_path: Path,
    progress_callback: Callable[[int, int], None] | None,
) -> ConversionResult:
    import libvisio_ng

    with tempfile.TemporaryDirectory(prefix="visio_viewer_") as tmp_dir:
        tmp_path = Path(tmp_dir)
        log.info(f"Temp dir: {tmp_path}")
        log.info(f"Calling libvisio_ng.convert({file_path})")

        result = libvisio_ng.convert(str(file_path), output_dir=str(tmp_path))
        log.info(f"convert() returned: {type(result)} = {result!r}")

        if isinstance(result, (list, tuple)) and result:
            svg_files = sorted(
                [Path(p) for p in result if str(p).endswith(".svg")],
                key=_page_sort_key,
            )
        else:
            svg_files = sorted(tmp_path.glob("*.svg"), key=_page_sort_key)

        all_files = list(tmp_path.iterdir())
        log.info(f"Files in tmp: {[f.name for f in all_files]}")
        log.info(f"SVG files found: {[f.name for f in svg_files]}")

        if not svg_files:
            file_list = ", ".join(f.name for f in all_files) if all_files else "（なし）"
            msg = (f"SVGの生成に失敗しました。\n\n"
                   f"出力ディレクトリ: {tmp_path}\n"
                   f"生成されたファイル: {file_list}")
            log.error(msg)
            return ConversionResult(error=msg)

        total = len(svg_files)
        pages: list[bytes] = []
        page_names: list[str] = []

        for i, svg_file in enumerate(svg_files):
            if progress_callback:
                progress_callback(i + 1, total)
            svg_bytes = svg_file.read_bytes()
            log.info(f"Page {i+1}: {svg_file.name} ({len(svg_bytes)} bytes)")
            if not svg_bytes:
                svg_bytes = b'<svg xmlns="http://www.w3.org/2000/svg"><text y="20">Page empty</text></svg>'
            pages.append(svg_bytes)
            page_names.append(_make_page_name(svg_file, i))

        log.info(f"Conversion complete: {total} pages")
        return ConversionResult(pages=pages, page_names=page_names)


def _page_sort_key(path: Path) -> tuple[int, str]:
    name = path.stem
    digits = "".join(c for c in name if c.isdigit())
    return (int(digits) if digits else 0, name)


def _make_page_name(svg_file: Path, index: int) -> str:
    stem = svg_file.stem
    clean = stem.replace("-", " ").replace("_", " ").strip()
    return clean if clean else f"ページ {index + 1}"


def get_page_names_from_vsdx(file_path: str | Path) -> list[str]:
    file_path = Path(file_path)
    if file_path.suffix.lower() != ".vsdx":
        return []
    try:
        import xml.etree.ElementTree as ET
        with zipfile.ZipFile(file_path) as z:
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
