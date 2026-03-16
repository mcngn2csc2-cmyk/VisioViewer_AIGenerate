# -*- mode: python ; coding: utf-8 -*-
#
# visio_viewer.spec - PyInstaller ビルド設定
#
# 使い方:
#   cd build
#   pyinstaller visio_viewer.spec
#
# 生成物: dist/VisioViewer/VisioViewer.exe (フォルダ配布)
#         または --onefile オプションで単一EXEも可能

import sys
from pathlib import Path

SRC_DIR = str(Path("../src").resolve())
RESOURCES_DIR = str(Path("../resources").resolve())
ICON_PATH = str(Path("../resources/icon.ico").resolve())

block_cipher = None

a = Analysis(
    [str(Path(SRC_DIR) / "main.py")],
    pathex=[SRC_DIR],
    binaries=[],
    datas=[
        # リソースファイルをEXEに同梱
        (RESOURCES_DIR, "resources"),
    ],
    hiddenimports=[
        # libvisio-ng の動的インポートに備えて明示
        "libvisio_ng",
        "olefile",
        "xml.etree.ElementTree",
        "zipfile",
        # PySide6 SVG モジュール
        "PySide6.QtSvg",
        "PySide6.QtSvgWidgets",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 不要なQtモジュールを除外してファイルサイズを削減
        "PySide6.QtWebEngine",
        "PySide6.QtWebEngineWidgets",
        "PySide6.QtWebEngineCore",
        "PySide6.QtMultimedia",
        "PySide6.QtMultimediaWidgets",
        "PySide6.Qt3DCore",
        "PySide6.Qt3DRender",
        "PySide6.QtDataVisualization",
        "PySide6.QtCharts",
        # 標準ライブラリの不要モジュール
        "unittest",
        "email",
        "html",
        "http",
        "urllib",
        "tkinter",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="VisioViewer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                         # UPX圧縮（インストール済みの場合）
    console=False,                    # コンソールウィンドウを非表示
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_PATH if Path(ICON_PATH).exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="VisioViewer",
)
