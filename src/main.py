"""
main.py - Visio Viewer エントリポイント
"""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from main_window import MainWindow

APP_VERSION = "1.0.0"


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Visio Viewer")
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("VisioViewer")

    # アプリアイコン（resources/icon.ico があれば設定）
    icon_path = Path(__file__).parent.parent / "resources" / "icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow()
    window.show()

    # コマンドライン引数でファイルを直接開く
    # 例: visio_viewer.exe diagram.vsdx
    args = sys.argv[1:]
    if args:
        file_path = Path(args[0])
        if file_path.exists() and file_path.suffix.lower() in (".vsd", ".vsdx"):
            window.load_file(str(file_path))

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
