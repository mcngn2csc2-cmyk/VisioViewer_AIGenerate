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

echo [1/5] Creating virtual environment...
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

echo [2/5] Installing dependencies...
call .venv_build\Scripts\activate.bat

pip install --upgrade pip >nul

echo   Installing libvisio-ng...
pip install libvisio-ng
if errorlevel 1 (
    echo [ERROR] Failed to install libvisio-ng.
    echo         Check your internet connection and try again.
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

echo [3/5] Cleaning old build artifacts...
if exist "build\dist\VisioViewer" rmdir /s /q "build\dist\VisioViewer"
if exist "build\build\VisioViewer" rmdir /s /q "build\build\VisioViewer"

echo [4/5] Building with PyInstaller (this may take a few minutes)...
cd build
pyinstaller visio_viewer.spec
if errorlevel 1 (
    echo [ERROR] PyInstaller build failed.
    pause
    exit /b 1
)
cd ..

echo [5/5] Build complete!
echo.
echo  Output: build\dist\VisioViewer\VisioViewer.exe
echo.

REM --- Show output size ---
for /f "tokens=3" %%a in ('dir /s "build\dist\VisioViewer" ^| findstr "File(s)"') do (
    set SIZE=%%a
)
echo  Total size: %SIZE% bytes

echo.
echo Success! Distribute the build\dist\VisioViewer\ folder.
echo.
pause
