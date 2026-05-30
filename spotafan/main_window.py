from PySide6.QtCore import Qt,Signal
import json,os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QFrame, QLabel,
    QSizePolicy, QApplication,
)

from spotafan.config import Config
from spotafan.Lang import LANG
from spotafan.database import Database
from spotafan.player.engine import PlayerEngine
from spotafan.player.playlist import PlaylistManager
from spotafan.downloader.manager import DownloadManager
from spotafan.library.manager import LibraryManager
from spotafan.ui.player_bar import PlayerBar
from spotafan.ui.library_view import LibraryView
from spotafan.ui.search_view import SearchView
from spotafan.ui.download_view import DownloadView
from spotafan.ui.style import DARK_STYLE
from spotafan.ui.style import LIGHT_STYLE


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        Config.load_settings()
        LANG.load_settings()

        self._db = Database()
        self._engine = PlayerEngine(self)
        self._playlist_mgr = PlaylistManager(self._db, self)
        self._library_mgr = LibraryManager(self._db, self)
        self._downloader = DownloadManager(self._db, self)

        self._setup_window()
        self._setup_ui()
        self._connect_signals()
        self._restore_volume()


    def _setup_window(self):
        self.setWindowTitle(f"{Config.APP_NAME} v{Config.VERSION}")
        self.setMinimumSize(1000, 650)
        self.resize(1200, 750)
        self.setStyleSheet(DARK_STYLE if Config.get("theme") == "dark" else LIGHT_STYLE)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Content area: sidebar + main content
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Logo / Brand
        brand = QLabel("   SpotAFan")
        brand.setStyleSheet("""
            font-size: 20px; font-weight: bold; color: #1db954;
            padding: 20px 16px;
        """)
        sidebar_layout.addWidget(brand)
        
        self._nav_btns = {}
        nav_items = [
            ("library", f"🎵  {LANG.get("your_playlist")}"),
            ("search", f"🔍  {LANG.get("explore")}"),
            ("downloads", f"⬇  {LANG.get("download")}"),
        ]
        for key, label in nav_items:
            btn = QPushButton(label)
            btn.setObjectName("iconic")
            btn.setCheckable(True)
            btn.setFixedHeight(48)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left; padding: 12px 16px;
                    font-size: 14px; border-radius: 0;
                    border: none; background: transparent; color: #b3b3b3;
                }
                QPushButton:hover { color: #ffffff; }
                QPushButton:checked {
                    color: #ffffff; font-weight: bold;
                    border-left: 3px solid #1db954;
                    background-color: #1a1a1a;
                }
            """)
            self._nav_btns[key] = btn
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # Bottom sidebar: settings
        
        self.settings_btn = QPushButton(f"⚙  {LANG.get("settings")}")
        self.settings_btn.setObjectName("iconic")
        self.settings_btn.setFixedHeight(48)
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                text-align: left; padding: 12px 16px;
                font-size: 14px; border-radius: 0;
                border: none; background: transparent; color: #b3b3b3;
            }
            QPushButton:hover { color: #ffffff; }
        """)
        sidebar_layout.addWidget(self.settings_btn)

        content_layout.addWidget(sidebar)

        # Main content area with stacked widget
        self._stack = QStackedWidget()
        self._stack.setStyleSheet("background: transparent;")

        self._library_view = LibraryView(self._library_mgr, self._db)
        self._search_view = SearchView(self._downloader)
        self._download_view = DownloadView(self._downloader)

        self._stack.addWidget(self._library_view)
        self._stack.addWidget(self._search_view)
        self._stack.addWidget(self._download_view)

        content_layout.addWidget(self._stack, stretch=1)
        main_layout.addWidget(content, stretch=1)

        # Player bar at bottom
        self._player_bar = PlayerBar(self._engine)
        main_layout.addWidget(self._player_bar)

        # Default to library view
        self._nav_btns["library"].setChecked(True)
        self._stack.setCurrentIndex(0)

    def _connect_signals(self):
        self._nav_btns["library"].clicked.connect(
            lambda: self._switch_view(0)
        )
        self._nav_btns["search"].clicked.connect(
            lambda: self._switch_view(1)
        )
        self._nav_btns["downloads"].clicked.connect(
            lambda: self._switch_view(2)
        )
        self.settings_btn.clicked.connect(
            lambda: self._switch_view(3)
        )

        self._library_view.play_song_requested.connect(self._play_song)
        self._download_view.song_ready.connect(self._library_view.refresh)

    def _switch_view(self, index):
        self._stack.setCurrentIndex(index)
        for i, (key, btn) in enumerate(self._nav_btns.items()):
            names = ["library", "search", "downloads","settings"]
            btn.setChecked(key == names[index])

    def _play_song(self, song):
        self._engine.set_playlist(self._library_mgr.get_all_songs())
        songs = self._library_mgr.get_all_songs()
        for i, s in enumerate(songs):
            if s["id"] == song["id"]:
                self._engine.set_playlist(songs, start_index=i)
                break
        else:
            self._engine.play_song(song)

    def _restore_volume(self):
        vol = Config.get("volume", 80)
        self._engine.volume = vol

    def closeEvent(self, event):
        CLOSE=True
        Config.set("volume", self._engine.volume)
        self._engine.cleanup()
        super().closeEvent(event)
