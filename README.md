# Visio Viewer

VSD / VSDX 形式の Visio ファイルを閲覧するためのシンプルなデスクトップアプリケーションです。
編集機能はなく、閲覧専用です。

## 機能

- **.vsdx** / **.vsd** ファイルの表示
- 複数ページのナビゲーション（前/次ボタン、サムネイルクリック）
- ズームイン/アウト（Ctrl + マウスホイール）
- 全体表示リセット（Ctrl + 0）
- ドラッグ＆ドロップでファイルを開く
- コマンドライン引数でファイルを直接開く（ファイル関連付け対応）
- ウィンドウサイズ・レイアウトの記憶

## 動作環境

- Windows 10 / 11（64bit）
- Python 3.11 以上（開発時のみ必要、EXE配布版は不要）

## 使い方

### EXE で実行（配布版）

```
dist\VisioViewer\VisioViewer.exe
```

`VisioViewer.exe` に .vsdx/.vsd ファイルをドラッグ&ドロップして起動することもできます。

### Python で実行（開発時）

```bash
# 依存パッケージのインストール
pip install -r requirements.txt

# 起動
python src/main.py

# ファイルを指定して起動
python src/main.py path/to/diagram.vsdx
```

## EXE ビルド方法

Windows 上で以下を実行します：

```cmd
build\build_exe.bat
```

`dist\VisioViewer\` フォルダに `VisioViewer.exe` が生成されます。
このフォルダごとコピーして配布できます（Python のインストール不要）。

## 技術スタック

| コンポーネント | ライブラリ |
|---|---|
| Visio変換エンジン | [libvisio-ng](https://github.com/yeager/libvisio-ng) (GPL-3+) |
| GUI フレームワーク | [PySide6](https://doc.qt.io/qtforpython/) (LGPL) |
| EXEパッケージ | [PyInstaller](https://pyinstaller.org/) |

## ライセンス

本アプリは [libvisio-ng](https://github.com/yeager/libvisio-ng) (GPL-3+) を使用しているため、
GPL-3 ライセンスに従って配布されます。

## プロジェクト構成

```
VisioViewer_AIGenerate/
├── src/
│   ├── main.py              # エントリポイント
│   ├── main_window.py       # メインウィンドウ
│   ├── svg_viewer.py        # SVG表示ウィジェット（ズーム・パン）
│   ├── thumbnail_panel.py   # ページサムネイルパネル
│   ├── converter.py         # libvisio-ng ラッパー
│   └── worker.py            # バックグラウンド変換スレッド
├── resources/
│   └── icon.ico             # アプリアイコン（任意）
├── build/
│   ├── visio_viewer.spec    # PyInstaller 設定
│   └── build_exe.bat        # Windows ビルドスクリプト
├── requirements.txt
└── README.md
```
