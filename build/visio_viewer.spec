# -*- mode: python ; coding: utf-8 -*-
#
# visio_viewer.spec - PyInstaller build configuration
#
# Output: dist/VisioViewer/VisioViewer.exe  (run THIS, not build/VisioViewer/)

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_data_files

SRC_DIR = str(Path("../src").resolve())
RESOURCES_DIR = Path("../resources").resolve()
ICON_PATH = RESOURCES_DIR / "icon.ico"

block_cipher = None

# --- Bundle libvisio_ng by finding its install path directly ---
try:
    import libvisio_ng as _lv
    _lv_dir = Path(_lv.__file__).parent
    libvisio_datas = [(str(_lv_dir), "libvisio_ng")]
    print(f"[spec] libvisio_ng found at: {_lv_dir}")
except ImportError:
    raise SystemExit("[spec] ERROR: libvisio_ng is not installed in this Python env.\n"
                     "Run the bat file to build (it installs into .venv_build).")

# --- Bundle olefile (needed for .vsd binary format) ---
try:
    import olefile as _ol
    _ol_dir = Path(_ol.__file__).parent
    olefile_datas = [(str(_ol_dir), "olefile")]
    print(f"[spec] olefile found at: {_ol_dir}")
except ImportError:
    olefile_datas = []
    print("[spec] WARNING: olefile not found, .vsd support may be limited.")

# --- Resources folder (optional) ---
extra_datas = []
if RESOURCES_DIR.exists() and any(RESOURCES_DIR.iterdir()):
    extra_datas.append((str(RESOURCES_DIR), "resources"))

a = Analysis(
    [str(Path(SRC_DIR) / "main.py")],
    pathex=[SRC_DIR],
    binaries=[],
    datas=libvisio_datas + olefile_datas + extra_datas,
    hiddenimports=[
        "libvisio_ng",
        "olefile",
        "xml.etree.ElementTree",
        "zipfile",
        "PySide6.QtSvg",
        "PySide6.QtSvgWidgets",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "PySide6.QtWebEngine",
        "PySide6.QtWebEngineWidgets",
        "PySide6.QtWebEngineCore",
        "PySide6.QtMultimedia",
        "PySide6.QtMultimediaWidgets",
        "PySide6.Qt3DCore",
        "PySide6.Qt3DRender",
        "PySide6.QtDataVisualization",
        "PySide6.QtCharts",
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
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ICON_PATH) if ICON_PATH.exists() else None,
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
