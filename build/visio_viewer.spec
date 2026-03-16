# -*- mode: python ; coding: utf-8 -*-
#
# visio_viewer.spec - PyInstaller build configuration
#
# Output: dist/VisioViewer/VisioViewer.exe
# NOTE: libvisio_ng and olefile are copied into _internal/ by build_exe.bat
#       after PyInstaller finishes (more reliable than spec-based bundling).

from pathlib import Path

SRC_DIR = str(Path("../src").resolve())
RESOURCES_DIR = Path("../resources").resolve()
ICON_PATH = RESOURCES_DIR / "icon.ico"

block_cipher = None

extra_datas = []
if RESOURCES_DIR.exists() and any(RESOURCES_DIR.iterdir()):
    extra_datas.append((str(RESOURCES_DIR), "resources"))

a = Analysis(
    [str(Path(SRC_DIR) / "main.py")],
    pathex=[SRC_DIR],
    binaries=[],
    datas=extra_datas,
    hiddenimports=[
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
