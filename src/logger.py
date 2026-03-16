"""
logger.py - ファイルへのログ出力（クラッシュ時の診断用）
EXE と同じフォルダに visio_viewer.log として出力される。
"""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path


def get_log_path() -> Path:
    if getattr(sys, "frozen", False):
        # PyInstaller EXE として実行中
        base = Path(sys.executable).parent
    else:
        # 通常の Python 実行
        base = Path(__file__).parent.parent
    return base / "visio_viewer.log"


def setup() -> logging.Logger:
    log_path = get_log_path()
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8", mode="w"),
        ],
    )
    logger = logging.getLogger("visio_viewer")
    logger.info(f"Log file: {log_path}")
    logger.info(f"Python: {sys.version}")
    logger.info(f"Executable: {sys.executable}")
    return logger


log = setup()
