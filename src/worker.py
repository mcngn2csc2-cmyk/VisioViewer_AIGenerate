"""
worker.py - Visio変換をバックグラウンドスレッドで実行する QThread ワーカー
"""
from __future__ import annotations

import traceback
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from converter import ConversionResult, convert_visio
from logger import log


class ConversionWorker(QThread):
    """
    ファイル変換をUIスレッドをブロックせずに実行する QThread サブクラス。

    シグナル:
        progress(current, total) - ページごとの進捗
        finished(result)         - 変換完了（成功・失敗どちらも）
    """

    progress = Signal(int, int)           # (current_page, total_pages)
    finished = Signal(ConversionResult)   # 変換結果

    def __init__(self, file_path: str | Path) -> None:
        super().__init__()
        self._file_path = Path(file_path)
        self._cancelled = False

    def run(self) -> None:
        """スレッドのメイン処理"""
        try:
            result = convert_visio(
                self._file_path,
                progress_callback=self._on_progress,
            )
        except BaseException as e:
            tb = traceback.format_exc()
            log.critical(f"Worker thread crashed:\n{tb}")
            result = ConversionResult(error=f"クラッシュ:\n{e}\n\n{tb}")
        if not self._cancelled:
            self.finished.emit(result)

    def cancel(self) -> None:
        """変換をキャンセルする（実行中スレッドには割り込まない）"""
        self._cancelled = True

    def _on_progress(self, current: int, total: int) -> None:
        if not self._cancelled:
            self.progress.emit(current, total)
