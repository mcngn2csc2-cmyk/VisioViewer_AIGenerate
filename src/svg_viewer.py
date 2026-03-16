"""
svg_viewer.py - SVG を表示する QGraphicsView ウィジェット（ズーム・パン対応）
"""
from __future__ import annotations

from PySide6.QtCore import Qt, QByteArray, QRectF, Signal
from PySide6.QtGui import (
    QWheelEvent,
    QKeySequence,
    QShortcut,
    QColor,
    QPainter,
    QBrush,
    QPen,
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtSvgWidgets import QGraphicsSvgItem
from PySide6.QtWidgets import (
    QGraphicsScene,
    QGraphicsView,
    QWidget,
)

# ズームの最小・最大倍率
ZOOM_MIN = 0.05
ZOOM_MAX = 20.0
ZOOM_STEP = 1.15  # Ctrl+ホイール 1段あたりの倍率


class SvgViewer(QGraphicsView):
    """
    SVG ファイルを表示する GraphicsView。
    - Ctrl + ホイール: ズームイン/アウト
    - マウスドラッグ: パン（スクロール）
    - Ctrl+0: 全体表示にリセット
    - Ctrl++/−: ズーム
    """

    zoom_changed = Signal(float)  # ズーム倍率が変わったとき emit

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._scene = QGraphicsScene(self)
        self._svg_item: QGraphicsSvgItem | None = None
        self._zoom_factor: float = 1.0
        self._is_initial_fit: bool = True  # True while no manual zoom has been applied

        self.setScene(self._scene)
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.SmoothPixmapTransform
        )
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setBackgroundBrush(QBrush(QColor("#F0F0F0")))  # 薄いグレー背景

        # キーボードショートカット
        QShortcut(QKeySequence("Ctrl+0"), self, self.fit_to_window)
        QShortcut(QKeySequence("Ctrl+="), self, self.zoom_in)
        QShortcut(QKeySequence("Ctrl++"), self, self.zoom_in)
        QShortcut(QKeySequence("Ctrl+-"), self, self.zoom_out)

    # ─────────────────────────────────────────────
    # 公開API
    # ─────────────────────────────────────────────

    def load_svg(self, svg_data: bytes) -> None:
        """SVG バイト列を読み込んで表示する"""
        self._scene.clear()
        self._svg_item = None

        renderer = QSvgRenderer(QByteArray(svg_data))
        if not renderer.isValid():
            self._scene.addText("SVGの読み込みに失敗しました（不正なSVGデータ）")
            return

        default_size = renderer.defaultSize()
        view_box = renderer.viewBoxF()

        # 表示サイズを決定: viewBox > defaultSize > フォールバック の優先順
        if not view_box.isNull() and view_box.width() > 0:
            rect = view_box
        elif default_size.width() > 0 and default_size.height() > 0:
            rect = QRectF(0, 0, default_size.width(), default_size.height())
        else:
            self._scene.addText("SVGのサイズが取得できませんでした")
            return

        item = QGraphicsSvgItem()
        item.setSharedRenderer(renderer)
        item.setCacheMode(item.CacheMode.DeviceCoordinateCache)

        self._scene.addItem(item)
        self._svg_item = item
        self._scene.setSceneRect(rect)

        # ビューをリセットして全体表示
        self.resetTransform()
        self._zoom_factor = 1.0
        self._is_initial_fit = True
        self.fit_to_window()

    def clear(self) -> None:
        """表示内容をクリアする"""
        self._scene.clear()
        self._svg_item = None
        self._zoom_factor = 1.0

    def fit_to_window(self) -> None:
        """現在のウィンドウサイズに合わせて全体表示する"""
        if self._svg_item is None:
            return
        self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        # 実際の倍率を計算して記録
        self._zoom_factor = self.transform().m11()
        self.zoom_changed.emit(self._zoom_factor)

    def zoom_in(self) -> None:
        self._apply_zoom(ZOOM_STEP)

    def zoom_out(self) -> None:
        self._apply_zoom(1.0 / ZOOM_STEP)

    @property
    def zoom_percent(self) -> int:
        """現在のズーム倍率をパーセント（整数）で返す"""
        return int(self._zoom_factor * 100)

    # ─────────────────────────────────────────────
    # イベントオーバーライド
    # ─────────────────────────────────────────────

    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            factor = ZOOM_STEP if delta > 0 else 1.0 / ZOOM_STEP
            self._apply_zoom(factor)
            event.accept()
        else:
            super().wheelEvent(event)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        # ウィンドウリサイズ時に初期表示だった場合は追従する
        if self._svg_item is not None and self._is_initial_fit:
            self.fit_to_window()

    # ─────────────────────────────────────────────
    # 内部処理
    # ─────────────────────────────────────────────

    def _apply_zoom(self, factor: float) -> None:
        new_zoom = self._zoom_factor * factor
        if new_zoom < ZOOM_MIN or new_zoom > ZOOM_MAX:
            return
        self.scale(factor, factor)
        self._zoom_factor = new_zoom
        self._is_initial_fit = False  # User has manually zoomed
        self.zoom_changed.emit(self._zoom_factor)
