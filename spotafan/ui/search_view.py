from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QFrame, QProgressBar,
    QScrollArea,
)

from spotafan.config import Config


class SearchView(QFrame):
    song_download_requested = Signal(dict)

    def __init__(self, download_manager, parent=None):
        super().__init__(parent)
        self._downloader = download_manager
        self._results = []
        self.setObjectName("card")
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Search & Download")
        title.setObjectName("header")
        layout.addWidget(title)

        # Search row
        search_row = QHBoxLayout()
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search for songs on YouTube...")
        search_row.addWidget(self._search_input, stretch=1)

        self._search_btn = QPushButton("🔍 Search")
        self._search_btn.setFixedWidth(120)
        search_row.addWidget(self._search_btn)
        layout.addLayout(search_row)

        # Results area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        self._results_container = QWidget()
        self._results_layout = QVBoxLayout(self._results_container)
        self._results_layout.setSpacing(8)
        self._results_layout.setContentsMargins(0, 0, 0, 0)

        self._empty_label = QLabel(
            "Search for music to download.\nUse the search bar above to find songs."
        )
        self._empty_label.setObjectName("subtitle")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setMinimumHeight(200)
        self._results_layout.addWidget(self._empty_label)
        self._results_layout.addStretch()

        scroll.setWidget(self._results_container)
        layout.addWidget(scroll, stretch=1)

        self._status_label = QLabel("")
        self._status_label.setObjectName("subtitle")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._status_label)

    def _connect_signals(self):
        self._search_btn.clicked.connect(self._do_search)
        self._search_input.returnPressed.connect(self._do_search)
        self._downloader.search_completed.connect(self._on_search_results)
        self._downloader.search_error.connect(
            lambda err: self._status_label.setText(f"Search error: {err}")
        )

    def _do_search(self):
        query = self._search_input.text().strip()
        if not query:
            return
        self._status_label.setText("Searching...")
        self._clear_results()
        self._downloader.search(query)

    def _clear_results(self):
        while self._results_layout.count():
            item = self._results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _on_search_results(self, results):
        self._results = results
        self._clear_results()
        self._status_label.setText(
            f"Found {len(results)} result{'s' if len(results) != 1 else ''}"
        )

        if not results:
            self._results_layout.addWidget(self._empty_label)
            self._results_layout.addStretch()
            return

        for res in results:
            card = self._create_result_card(res)
            self._results_layout.addWidget(card)

        self._results_layout.addStretch()

    def _create_result_card(self, result):
        card = QFrame()
        card.setObjectName("card")
        card.setFixedHeight(72)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setStyleSheet("""
            QFrame#card {
                background-color: #181818; border-radius: 6px;
                padding: 8px 12px;
            }
            QFrame#card:hover { background-color: #282828; }
        """)

        row = QHBoxLayout(card)
        row.setContentsMargins(12, 8, 12, 8)
        row.setSpacing(12)

        # Thumbnail placeholder
        thumb = QLabel("🎵")
        thumb.setFixedSize(48, 48)
        thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumb.setStyleSheet(
            "background-color: #333; border-radius: 4px; font-size: 20px;"
        )
        row.addWidget(thumb)

        # Info
        info = QVBoxLayout()
        info.setSpacing(2)
        title = QLabel(result.get("title", "Unknown"))
        title.setStyleSheet("font-weight: bold; font-size: 13px; color: #ffffff;")
        title.setWordWrap(True)
        info.addWidget(title)

        sub = QLabel(f"{result.get('artist', 'Unknown')}  ·  "
                     f"{self._format_time(result.get('duration', 0))}")
        sub.setStyleSheet("font-size: 11px; color: #b3b3b3;")
        info.addWidget(sub)
        row.addLayout(info, stretch=1)

        # Download button
        download_btn = QPushButton("Download")
        download_btn.setFixedSize(105, 32)
        download_btn.setStyleSheet("""
            QPushButton {
                background-color: #1db954; color: #ffffff;
                border: none; border-radius: 16px;
                font-size: 12px; font-weight: bold;
            }
            QPushButton:hover { background-color: #1ed760; }
        """)
        download_btn.clicked.connect(
            lambda checked, r=result: self._download_song(r)
        )
        row.addWidget(download_btn)

        return card

    def _download_song(self, result):
        self._downloader.start_download(result)
        self._status_label.setText(
            f'Downloading: {result.get("title", "")}...'
        )

    @staticmethod
    def _format_time(seconds):
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m}:{s:02d}"
