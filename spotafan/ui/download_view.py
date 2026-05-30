from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar,
    QFrame, QAbstractItemView,
)
from PySide6.QtGui import QColor, QPalette
from spotafan.Lang import LANG


class DownloadView(QFrame):
    song_ready = Signal(dict)

    def __init__(self, download_manager, parent=None):
        super().__init__(parent)
        self._downloader = download_manager
        self.setObjectName("card")
        self._setup_ui()
        self._connect_signals()
        self._refresh()
        LANG.load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Download")
        title.setObjectName("header")
        layout.addWidget(title)

        # Queue info
        info_row = QHBoxLayout()
        self._queue_count = QLabel(f"0 {LANG.get("active_downloads")}")
        self._queue_count.setObjectName("subtitle")
        info_row.addWidget(self._queue_count)
        info_row.addStretch()

        self._clear_btn = QPushButton(LANG.get("clear_complete"))
        self._clear_btn.setStyleSheet(
            "background-color: transparent; border: 1px solid #535353; "
            "border-radius: 16px; padding: 6px 16px; color: #ffffff; "
            "font-size: 12px;"
        )
        info_row.addWidget(self._clear_btn)
        layout.addLayout(info_row)

        # Table
        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels([
            "Title", "Artist", "Status", "Progress", ""
        ])
        self._table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self._table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self._table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Fixed
        )
        self._table.setColumnWidth(2, 120)
        self._table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.Fixed
        )
        self._table.setColumnWidth(3, 200)
        self._table.setColumnWidth(4, 40)
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setShowGrid(False)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setMinimumHeight(300)

        layout.addWidget(self._table)

    def _connect_signals(self):
        self._downloader.progress_updated.connect(self._on_progress)
        self._downloader.status_changed.connect(self._on_status_change)
        self._downloader.download_finished.connect(self._on_finished)
        self._downloader.download_error.connect(self._on_error)
        self._clear_btn.clicked.connect(self._clear_completed)

    def _refresh(self):
        downloads = self._downloader.get_downloads()
        active = [d for d in downloads if d["status"] in ("pending", "starting", "downloading", "processing")]
        self._queue_count.setText(f"{len(active)} active download{'s' if len(active) != 1 else ''}")
        self._populate_table(downloads)

    def _populate_table(self, downloads):
        self._table.setRowCount(len(downloads))
        for row, d in enumerate(downloads):
            title_item = QTableWidgetItem(d.get("title", "Unknown"))
            title_item.setData(Qt.ItemDataRole.UserRole, d["id"])
            self._table.setItem(row, 0, title_item)

            artist_item = QTableWidgetItem(d.get("artist", "Unknown Artist"))
            self._table.setItem(row, 1, artist_item)

            status = d.get("status", "unknown")
            status_item = QTableWidgetItem(status.capitalize())
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if status == "completed":
                status_item.setForeground(
                    QColor("#1db954")
                )
            elif status == "error":
                status_item.setForeground(
                    QColor("#e74c3c")
                )
            self._table.setItem(row, 2, status_item)

            # Progress bar
            prog_widget = QWidget()
            prog_layout = QHBoxLayout(prog_widget)
            prog_layout.setContentsMargins(8, 4, 8, 4)
            prog_bar = QProgressBar()
            prog_bar.setRange(0, 100)
            prog_bar.setValue(int(d.get("progress", 0)))
            prog_bar.setTextVisible(True)
            if status == "error":
                prog_bar.setStyleSheet(
                    "QProgressBar::chunk { background-color: #e74c3c; }"
                )
            elif status == "completed":
                prog_bar.setValue(100)
            prog_layout.addWidget(prog_bar)
            self._table.setCellWidget(row, 3, prog_widget)

            # Action button
            action_btn = QPushButton("✕" if status in ("completed", "error") else "")
            action_btn.setObjectName("iconic")
            action_btn.setFixedSize(32, 32)
            action_btn.setStyleSheet("font-size: 14px;")
            self._table.setCellWidget(row, 4, action_btn)

            self._table.setRowHeight(row, 48)

    def _on_progress(self, download_id, progress):
        for row in range(self._table.rowCount()):
            item = self._table.item(row, 0)
            if item and item.data(Qt.ItemDataRole.UserRole) == download_id:
                widget = self._table.cellWidget(row, 3)
                if widget:
                    bar = widget.findChild(QProgressBar)
                    if bar:
                        bar.setValue(int(progress))
                break

    def _on_status_change(self, download_id, status):
        for row in range(self._table.rowCount()):
            item = self._table.item(row, 0)
            if item and item.data(Qt.ItemDataRole.UserRole) == download_id:
                self._table.item(row, 2).setText(status.capitalize())
                if status == "completed":
                    self._table.item(row, 2).setForeground(
                        QColor("#1db954")
                    )
                break
        self._refresh()

    def _on_finished(self, download_id, song):
        self.song_ready.emit(song)
        self._refresh()

    def _on_error(self, download_id, error):
        for row in range(self._table.rowCount()):
            item = self._table.item(row, 0)
            if item and item.data(Qt.ItemDataRole.UserRole) == download_id:
                self._table.item(row, 2).setText("Error")
                self._table.item(row, 2).setForeground(
                    QColor("#e74c3c")
                )
                break
        self._refresh()

    def _clear_completed(self):
        downloads = self._downloader.get_downloads()
        for d in downloads:
            if d["status"] in ("completed", "error"):
                self._downloader._db.update_download(
                    d["id"],
                    status="cleared",
                )
        self._refresh()
