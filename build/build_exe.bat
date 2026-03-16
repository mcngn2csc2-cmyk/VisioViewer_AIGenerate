@echo off
REM ================================================================
REM build_exe.bat - Visio Viewer を Windows EXE にビルドするスクリプト
REM
REM 前提条件:
REM   - Python 3.11 以上がインストールされていること
REM   - このスクリプトは build\ フォルダで実行すること
REM
REM 使い方:
REM   build\build_exe.bat
REM ================================================================

setlocal enabledelayedexpansion

echo ====================================================
echo  Visio Viewer - Windows EXE ビルド
echo ====================================================
echo.

REM --- Python バージョン確認 ---
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python が見つかりません。Python 3.11+ をインストールしてください。
    pause
    exit /b 1
)

echo [1/5] 仮想環境の作成...
cd /d "%~dp0.."
if exist ".venv_build" (
    echo     既存の仮想環境を削除します...
    rmdir /s /q ".venv_build"
)
python -m venv .venv_build
if errorlevel 1 (
    echo [ERROR] 仮想環境の作成に失敗しました。
    pause
    exit /b 1
)

echo [2/5] 依存パッケージのインストール...
call .venv_build\Scripts\activate.bat

REM pyside6-essentials でサイズ最適化（フルのpyside6は不要）
pip install --upgrade pip >nul
pip install pyside6-essentials libvisio-ng pyinstaller
if errorlevel 1 (
    echo [ERROR] パッケージのインストールに失敗しました。
    pause
    exit /b 1
)

echo [3/5] 古いビルドを削除...
if exist "dist\VisioViewer" rmdir /s /q "dist\VisioViewer"
if exist "build\VisioViewer" rmdir /s /q "build\VisioViewer"

echo [4/5] PyInstaller でビルド中（数分かかります）...
cd build
pyinstaller visio_viewer.spec
if errorlevel 1 (
    echo [ERROR] ビルドに失敗しました。
    pause
    exit /b 1
)
cd ..

echo [5/5] ビルド完了！
echo.
echo  出力先: dist\VisioViewer\VisioViewer.exe
echo.

REM --- 出力サイズを表示 ---
for /f "tokens=3" %%a in ('dir /s "dist\VisioViewer" ^| findstr "File(s)"') do (
    set SIZE=%%a
)
echo  合計サイズ: %SIZE% バイト

echo.
echo ビルド成功！ dist\VisioViewer\ フォルダを配布してください。
echo.
pause
