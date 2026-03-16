"""
thumbnail_panel.py - ページサムネイルを一覧表示する左サイドパネル
"""
from __future__ import annotations

from PySide6.QtCore import Qt, QByteArray, QSize, Signal
from PySide6.QtGui import QImage, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

THUMBNAIL_WIDTH = 140
THUMBNAIL_HEIGHT = 100
PANEL_WIDTH = 160


class ThumbnailPanel(QWidget):
    """
    ページサムネイルを縦一列に並べるパネル。
    ユーザーがサムネイルをクリックすると page_selected シグナルが emit される。
    """

    page_selected = Signal(int)  # 選択されたページインデックス（0始まり）

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedWidth(PANEL_WIDTH)
        self.setMinimumWidth(PANEL_WIDTH)

        self._list = QListWidget()
        self._list.setIconSize(QSize(THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT))
        self._list.setSpacing(4)
        self._list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self._list.itemClicked.connect(self._on_item_clicked)

        header = QLabel("ページ")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(
            "font-weight: bold; padding: 4px; background: #DDEEFF; border-bottom: 1px solid #AABBCC;"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(header)
        layout.addWidget(self._list)

    # ─────────────────────────────────────────────
    # 公開API
    # ─────────────────────────────────────────────

    def set_pages(self, svg_list: list[bytes], page_names: list[str]) -> None:
        """全ページの SVG データを受け取り、サムネイルを生成して表示する"""
        self._list.clear()

        if len(svg_list) != len(page_names):
            raise ValueError(f"svg_list length ({len(svg_list)}) != page_names length ({len(page_names)})")

        for i, (svg_data, name) in enumerate(zip(svg_list, page_names)):
            pixmap = self._render_thumbnail(svg_data)
            item = QListWidgetItem(pixmap, f"{i + 1}. {name}")
            item.setData(Qt.ItemDataRole.UserRole, i)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setSizeHint(QSize(PANEL_WIDTH - 8, THUMBNAIL_HEIGHT + 24))
            self._list.addItem(item)

    def select_page(self, index: int) -> None:
        """指定ページを選択状態にする（シグナルは emit しない）"""
        if 0 <= index < self._list.count():
            self._list.blockSignals(True)
            self._list.setCurrentRow(index)
            self._list.blockSignals(False)
            self._list.scrollToItem(self._list.item(index))

    def clear(self) -> None:
        self._list.clear()

    # ─────────────────────────────────────────────
    # 内部処理
    # ─────────────────────────────────────────────

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        index = item.data(Qt.ItemDataRole.UserRole)
        if index is not None:
            self.page_selected.emit(index)

    @staticmethod
    def _render_thumbnail(svg_data: bytes) -> QPixmap:
        """SVG バイト列からサムネイル用 QPixmap を生成する"""
        renderer = QSvgRenderer(QByteArray(svg_data))
        if not renderer.isValid():
            return QPixmap(THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT)

        # アスペクト比を保ってサムネイルサイズに収める
        default_size = renderer.defaultSize()
        if default_size.width() > 0 and default_size.height() > 0:
            scale = min(
                THUMBNAIL_WIDTH / default_size.width(),
                THUMBNAIL_HEIGHT / default_size.height(),
            )
            w = int(default_size.width() * scale)
            h = int(default_size.height() * scale)
        else:
            w, h = THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT

        image = QImage(w, h, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.white)

        painter = QPainter(image)
        renderer.render(painter)
        painter.end()

        return QPixmap.fromImage(image)
