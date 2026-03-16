"""
main_window.py - Visio Viewer のメインウィンドウ
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from converter import ConversionResult
from svg_viewer import SvgViewer
from thumbnail_panel import ThumbnailPanel
from worker import ConversionWorker

APP_NAME = "Visio Viewer"
SUPPORTED_FORMATS = "Visio ファイル (*.vsdx *.vsd);;すべてのファイル (*.*)"
SETTINGS_KEY_LAST_DIR = "last_open_dir"
SETTINGS_KEY_GEOMETRY = "geometry"
SETTINGS_KEY_SPLITTER = "splitter_state"


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self._pages: list[bytes] = []
        self._page_names: list[str] = []
        self._current_page: int = 0
        self._worker: ConversionWorker | None = None

        self._settings = QSettings("VisioViewer", "VisioViewer")

        self._build_ui()
        self._restore_geometry()
        self.setAcceptDrops(True)

    # ─────────────────────────────────────────────
    # UI構築
    # ─────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setWindowTitle(APP_NAME)
        self.resize(1200, 800)

        # ─── メニューバー ───
        menu = self.menuBar()
        file_menu = menu.addMenu("ファイル(&F)")

        open_action = file_menu.addAction("開く(&O)…")
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.triggered.connect(self.open_file_dialog)

        file_menu.addSeparator()

        exit_action = file_menu.addAction("終了(&X)")
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)

        view_menu = menu.addMenu("表示(&V)")

        fit_action = view_menu.addAction("全体表示(&F)")
        fit_action.setShortcut(QKeySequence("Ctrl+0"))
        fit_action.triggered.connect(self._on_fit)

        zoom_in_action = view_menu.addAction("ズームイン(&I)")
        zoom_in_action.setShortcut(QKeySequence("Ctrl+="))
        zoom_in_action.triggered.connect(self._on_zoom_in)

        zoom_out_action = view_menu.addAction("ズームアウト(&O)")
        zoom_out_action.setShortcut(QKeySequence("Ctrl+-"))
        zoom_out_action.triggered.connect(self._on_zoom_out)

        # ─── ツールバー ───
        toolbar = QToolBar("メインツールバー")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        toolbar.addAction("📂 開く", self.open_file_dialog)
        toolbar.addSeparator()

        self._prev_btn = toolbar.addAction("◀ 前ページ", self._go_prev)
        self._prev_btn.setShortcut(QKeySequence("Left"))
        self._prev_btn.setEnabled(False)

        self._page_label = QLabel("  -  ")
        self._page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._page_label.setMinimumWidth(80)
        toolbar.addWidget(self._page_label)

        self._next_btn = toolbar.addAction("次ページ ▶", self._go_next)
        self._next_btn.setShortcut(QKeySequence("Right"))
        self._next_btn.setEnabled(False)

        toolbar.addSeparator()
        toolbar.addAction("🔍 全体表示", self._on_fit)
        toolbar.addAction("＋", self._on_zoom_in)
        toolbar.addAction("－", self._on_zoom_out)

        # ─── 中央ウィジェット ───
        self._thumbnail_panel = ThumbnailPanel()
        self._thumbnail_panel.page_selected.connect(self._go_to_page)

        self._svg_viewer = SvgViewer()
        self._svg_viewer.zoom_changed.connect(self._on_zoom_changed)

        # 初期表示：ファイルを開くよう促すプレースホルダー
        self._placeholder = self._make_placeholder()

        # ビューア領域（SVGビューア or プレースホルダー）
        self._view_stack = QVBoxLayout()
        self._view_stack.setContentsMargins(0, 0, 0, 0)
        self._view_stack.addWidget(self._svg_viewer)
        self._view_stack.addWidget(self._placeholder)
        self._svg_viewer.hide()

        view_container = QWidget()
        view_container.setLayout(self._view_stack)

        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.addWidget(self._thumbnail_panel)
        self._splitter.addWidget(view_container)
        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)
        self._splitter.setSizes([160, 1040])

        self.setCentralWidget(self._splitter)

        # ─── ステータスバー ───
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)

        self._status_label = QLabel("ファイルを開いてください")
        self._zoom_label = QLabel("")
        self._progress_bar = QProgressBar()
        self._progress_bar.setMaximumWidth(200)
        self._progress_bar.hide()

        status_bar.addWidget(self._status_label, 1)
        status_bar.addPermanentWidget(self._zoom_label)
        status_bar.addPermanentWidget(self._progress_bar)

    def _make_placeholder(self) -> QWidget:
        """ファイル未読み込み時のプレースホルダーウィジェット"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel("VSD / VSDX ファイルをここにドロップ\nまたは [ファイル] → [開く] で選択")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #888; font-size: 16px; padding: 40px;")

        btn = QPushButton("ファイルを開く…")
        btn.setFixedWidth(160)
        btn.clicked.connect(self.open_file_dialog)

        layout.addWidget(label)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
        return widget

    # ─────────────────────────────────────────────
    # ファイルオープン
    # ─────────────────────────────────────────────

    def open_file_dialog(self) -> None:
        last_dir = self._settings.value(SETTINGS_KEY_LAST_DIR, "")
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Visio ファイルを開く",
            last_dir,
            SUPPORTED_FORMATS,
        )
        if path:
            self._settings.setValue(SETTINGS_KEY_LAST_DIR, str(Path(path).parent))
            self.load_file(path)

    def load_file(self, file_path: str) -> None:
        """指定ファイルの変換・表示を開始する"""
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait()

        self._pages = []
        self._page_names = []
        self._current_page = 0
        self._thumbnail_panel.clear()
        self._svg_viewer.clear()
        self._update_nav_buttons()

        self._progress_bar.setValue(0)
        self._progress_bar.show()
        self._status_label.setText(f"変換中: {Path(file_path).name} …")
        self.setWindowTitle(f"{APP_NAME} - {Path(file_path).name}")

        self._worker = ConversionWorker(file_path)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_conversion_finished)
        self._worker.start()

    # ─────────────────────────────────────────────
    # ページナビゲーション
    # ─────────────────────────────────────────────

    def _go_to_page(self, index: int) -> None:
        if not self._pages or not (0 <= index < len(self._pages)):
            return
        self._current_page = index
        self._svg_viewer.load_svg(self._pages[index])
        self._thumbnail_panel.select_page(index)
        self._update_nav_buttons()
        self._update_page_label()

    def _go_prev(self) -> None:
        self._go_to_page(self._current_page - 1)

    def _go_next(self) -> None:
        self._go_to_page(self._current_page + 1)

    def _update_nav_buttons(self) -> None:
        count = len(self._pages)
        self._prev_btn.setEnabled(self._current_page > 0)
        self._next_btn.setEnabled(self._current_page < count - 1)

    def _update_page_label(self) -> None:
        count = len(self._pages)
        if count == 0:
            self._page_label.setText("  -  ")
        else:
            self._page_label.setText(f"  {self._current_page + 1} / {count}  ")

    # ─────────────────────────────────────────────
    # ズーム
    # ─────────────────────────────────────────────

    def _on_fit(self) -> None:
        self._svg_viewer.fit_to_window()

    def _on_zoom_in(self) -> None:
        self._svg_viewer.zoom_in()

    def _on_zoom_out(self) -> None:
        self._svg_viewer.zoom_out()

    def _on_zoom_changed(self, factor: float) -> None:
        self._zoom_label.setText(f"  {int(factor * 100)}%  ")

    # ─────────────────────────────────────────────
    # ワーカーシグナルハンドラ
    # ─────────────────────────────────────────────

    def _on_progress(self, current: int, total: int) -> None:
        self._progress_bar.setMaximum(total)
        self._progress_bar.setValue(current)

    def _on_conversion_finished(self, result: ConversionResult) -> None:
        self._progress_bar.hide()

        if not result.success:
            self._status_label.setText("エラーが発生しました")
            QMessageBox.critical(self, "変換エラー", result.error or "不明なエラー")
            return

        self._pages = result.pages
        self._page_names = result.page_names

        # サムネイルパネルを更新
        self._thumbnail_panel.set_pages(self._pages, self._page_names)

        # 1ページ目を表示
        self._placeholder.hide()
        self._svg_viewer.show()
        self._go_to_page(0)

        self._status_label.setText(
            f"{result.page_count} ページ読み込み完了"
        )

    # ─────────────────────────────────────────────
    # ドラッグ＆ドロップ
    # ─────────────────────────────────────────────

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().lower().endswith((".vsd", ".vsdx")):
                event.acceptProposedAction()
                return
        event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith((".vsd", ".vsdx")):
                self.load_file(file_path)

    # ─────────────────────────────────────────────
    # ウィンドウ状態の保存・復元
    # ─────────────────────────────────────────────

    def _restore_geometry(self) -> None:
        geometry = self._settings.value(SETTINGS_KEY_GEOMETRY)
        if geometry:
            self.restoreGeometry(geometry)
        splitter_state = self._settings.value(SETTINGS_KEY_SPLITTER)
        if splitter_state:
            self._splitter.restoreState(splitter_state)

    def closeEvent(self, event) -> None:
        self._settings.setValue(SETTINGS_KEY_GEOMETRY, self.saveGeometry())
        self._settings.setValue(SETTINGS_KEY_SPLITTER, self._splitter.saveState())
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait()
        super().closeEvent(event)
