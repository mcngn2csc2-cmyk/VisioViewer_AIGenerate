@echo off
REM ================================================================
REM build_exe.bat - Build Visio Viewer as Windows EXE
REM
REM Requirements:
REM   - Python 3.11 or later must be installed
REM   - Run this script from the project root or build\ folder
REM
REM Usage:
REM   build\build_exe.bat
REM ================================================================

setlocal enabledelayedexpansion

echo ====================================================
echo  Visio Viewer - Windows EXE Build
echo ====================================================
echo.

REM --- Check Python ---
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.11+.
    pause
    exit /b 1
)

echo [1/6] Creating virtual environment...
cd /d "%~dp0.."
if exist ".venv_build" (
    echo     Removing existing virtual environment...
    rmdir /s /q ".venv_build"
)
python -m venv .venv_build
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)

echo [2/6] Installing dependencies...
call .venv_build\Scripts\activate.bat

pip install --upgrade pip >nul

echo   Installing libvisio-ng...
pip install libvisio-ng
if errorlevel 1 (
    echo [ERROR] Failed to install libvisio-ng.
    pause
    exit /b 1
)

echo   Verifying libvisio-ng...
python -c "import libvisio_ng; print('  libvisio-ng OK:', libvisio_ng.__version__)"
if errorlevel 1 (
    echo [ERROR] libvisio-ng installed but cannot be imported.
    pause
    exit /b 1
)

echo   Installing PySide6...
pip install pyside6-essentials
if errorlevel 1 (
    echo [ERROR] Failed to install pyside6-essentials.
    pause
    exit /b 1
)

echo   Installing PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo [ERROR] Failed to install pyinstaller.
    pause
    exit /b 1
)

echo [3/6] Cleaning old build artifacts...
if exist "build\dist\VisioViewer" rmdir /s /q "build\dist\VisioViewer"
if exist "build\build\VisioViewer" rmdir /s /q "build\build\VisioViewer"

echo [4/6] Building with PyInstaller (this may take a few minutes)...
cd build
pyinstaller visio_viewer.spec
if errorlevel 1 (
    echo [ERROR] PyInstaller build failed.
    pause
    exit /b 1
)
cd ..

echo [5/6] Copying libvisio_ng and olefile into bundle...
python -c ^
  "import libvisio_ng, olefile, shutil, os, sys; ^
   base = os.path.join('build', 'dist', 'VisioViewer', '_internal'); ^
   pkgs = {'libvisio_ng': libvisio_ng, 'olefile': olefile}; ^
   [shutil.copytree(os.path.dirname(m.__file__), os.path.join(base, name), dirs_exist_ok=True) for name, m in pkgs.items()]; ^
   print('  Copied libvisio_ng and olefile to _internal/')"
if errorlevel 1 (
    echo [ERROR] Failed to copy packages into bundle.
    pause
    exit /b 1
)

echo [6/6] Verifying bundle...
if exist "build\dist\VisioViewer\_internal\libvisio_ng" (
    echo   libvisio_ng : OK
) else (
    echo   [WARN] libvisio_ng not found in bundle.
)
if exist "build\dist\VisioViewer\_internal\olefile" (
    echo   olefile     : OK
) else (
    echo   [WARN] olefile not found in bundle.
)

echo.
echo  +--------------------------------------------------+
echo  ^|  EXE is here:                                    ^|
echo  ^|  build\dist\VisioViewer\VisioViewer.exe          ^|
echo  ^|                                                  ^|
echo  ^|  Distribute the entire VisioViewer\ folder.     ^|
echo  +--------------------------------------------------+
echo.
pause
