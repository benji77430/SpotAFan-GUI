from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QFrame, QProgressBar,
    QScrollArea,
)
import requests
from spotafan.config import Config
from spotafan.Lang import LANG
import socket
def check_internet(ip="8.8.8.8",port=53,timeout=0.4):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((ip,port))
        return True
    except socket.error as ex:
        print(ex)
        return False

class SearchView(QFrame):
    song_download_requested = Signal(dict)

    def __init__(self, download_manager, parent=None):
        super().__init__(parent)
        self.internet=check_internet()
        self._downloader = download_manager
        self._results = []
        self.setObjectName("card")
        self._setup_ui()
        self._connect_signals()
        LANG.load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel(LANG.get("search&download"))
        title.setObjectName("header")
        layout.addWidget(title)

        # Search row
        search_row = QHBoxLayout()
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(LANG.get("searchonyt"))
        search_row.addWidget(self._search_input, stretch=1)

        self._search_btn = QPushButton(f"🔍 {LANG.get('search')}")
        self._search_btn.setFixedWidth(130)
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
            LANG.get("nosearchtext") if self.internet else LANG.get("nointernetsearch")
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
        if self.internet:
            query = self._search_input.text().strip()
            if not query:
                return
            self._status_label.setText(LANG.get("searching"))
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
        
        if not results:
            self._status_label.setText("Found 0 results")
            self._results_layout.addWidget(self._empty_label)
            self._results_layout.addStretch()
            return

        self._status_label.setText(
            f"Found {len(results)} result{'s' if len(results) != 1 else ''}"
        )

        # On parcourt chaque résultat et on cherche la cover si YouTube n'en fournit pas
        for res in results:
            thumb_url = res.get("thumbnail", "")
            if not thumb_url:
                # On extrait proprement le titre et l'artiste de chaque chanson retournée
                t = res.get("title", "")
                a = res.get("artist", "")
                thumb_url = self.fetch_track_cover(t, a)
                res["thumbnail"] = thumb_url  # On l'enregistre dans le dictionnaire

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

        # Image de miniature (Label)
        thumb_label = QLabel()
        thumb_label.setFixedSize(48, 48)
        thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Chargement de l'image (Locale ou Distante via iTunes/YouTube)
        thumb_url = result.get("thumbnail", "")
        loaded_successfully = False
        
        if thumb_url:
            try:
                from PySide6.QtGui import QPixmap
                pixmap = QPixmap()
                response = requests.get(thumb_url, timeout=0.4)
                if response.status_code == 200 and pixmap.loadFromData(response.content):
                    thumb_label.setPixmap(
                        pixmap.scaled(
                            48, 48,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation,
                        )
                    )
                    loaded_successfully = True
            except Exception:
                pass

        if not loaded_successfully:
            thumb_label.setText("🎵")
            thumb_label.setStyleSheet(
                "background-color: #333; border-radius: 4px; font-size: 20px; color: #ffffff;"
            )

        row.addWidget(thumb_label)

        # Info
        info = QVBoxLayout()
        info.setSpacing(2)
        title = QLabel(result.get("title", LANG.get("unknown_track")))
        title.setStyleSheet("font-weight: bold; font-size: 13px; color: #ffffff;")
        title.setWordWrap(True)
        info.addWidget(title)

        sub = QLabel(f"{result.get('artist', LANG.get('unknown_artist'))}  ·  "
                     f"{self._format_time(result.get('duration', 0))}")
        sub.setStyleSheet("font-size: 11px; color: #b3b3b3;")
        info.addWidget(sub)
        row.addLayout(info, stretch=1)

        # Download button
        download_btn = QPushButton(LANG.get("download"))
        download_btn.setFixedSize(105, 32)
        download_btn.setStyleSheet("""
            QPushButton {
                background-color: #1db954; color: #ffffff;
                border: none; border-radius: 16px;
                font-size: 11px; font-weight: bold;
            }
            QPushButton:hover { background-color: #1ed760; }
        """)
        download_btn.clicked.connect(
            lambda checked, r=result: self._download_song(r)
        )
        row.addWidget(download_btn)

        return card

    @staticmethod
    def fetch_track_cover(title, artist=""):
        """Recherche automatique via l'API publique et gratuite d'iTunes."""
        if not title or title == LANG.get("unknown_track") or not check_internet():
            return ""
        query = f"{title} {artist}".strip()
        url = f"https://itunes.apple.com/search?term={requests.utils.quote(query)}&entity=song&limit=1"
        try:
            response = requests.get(url, timeout=0.4)
            if response.status_code == 200:
                data = response.json()
                if data.get("resultCount", 0) > 0:
                    cover_url = data["results"][0]["artworkUrl100"]
                    return cover_url.replace("100x100bb", "600x600bb")
        except Exception as e:
            print(f"Erreur de jaquette de recherche: {e}")
        return ""

    def _download_song(self, result):
        self._downloader.start_download(result)
        self._status_label.setText(
            f'{LANG.get("downloading")} {result.get("title", "")}...'
        )

    @staticmethod
    def _format_time(seconds):
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m}:{s:02d}"