from PySide6.QtCore import Qt, Signal
import json, os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QFrame, QLabel,
    QSizePolicy, QApplication,
)
from PySide6.QtGui import QKeySequence, QShortcut
from spotafan.config import Config
from spotafan.Lang import LANG
from spotafan.database import Database
from spotafan.player.engine import PlayerEngine
from spotafan.player.playlist import PlaylistManager
from spotafan.downloader.manager import DownloadManager
from spotafan.library.manager import LibraryManager
from spotafan.ui.player_bar import PlayerBar
from spotafan.ui.library_view import LibraryView
from spotafan.ui.settings import SettingsPage  # Integrated cleanly
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
        self._setup_shortcuts()
        if Config.get("current_song", None) is not None:
            self._play_song(Config.get("current_song"), restart=True)

    def _setup_window(self):
        self.setWindowTitle(f"{Config.APP_NAME} v{Config.VERSION}")
        self.setMinimumSize(1000, 650)
        self.resize(1200, 750)
        self.setStyleSheet(DARK_STYLE if Config.get("theme", "dark") == "dark" else LIGHT_STYLE)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Sidebar Panel
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        brand = QLabel("   SpotAFan")
        brand.setStyleSheet("font-size: 20px; font-weight: bold; color: #1db954; padding: 20px 16px;")
        sidebar_layout.addWidget(brand)
        
        self._nav_btns = {}
        
        # Build Navigation Items Buttons dynamically
        self._library_btn = self._make_nav_btn("")
        self._search_btn = self._make_nav_btn("")
        self._downloads_btn = self._make_nav_btn("")
        self.settings_btn = self._make_nav_btn("")

        self._nav_btns["library"] = self._library_btn
        self._nav_btns["search"] = self._search_btn
        self._nav_btns["downloads"] = self._downloads_btn
        self._nav_btns["settings"] = self.settings_btn

        sidebar_layout.addWidget(self._library_btn)
        sidebar_layout.addWidget(self._search_btn)
        sidebar_layout.addWidget(self._downloads_btn)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(self.settings_btn)

        content_layout.addWidget(sidebar)

        # Main Central Presentation Window Stack
        self._stack = QStackedWidget()
        self._stack.setStyleSheet("background: transparent;")

        self._library_view = LibraryView(self._library_mgr, self._db)
        self._search_view = SearchView(self._downloader)
        self._download_view = DownloadView(self._downloader)
        self._settings_page = SettingsPage()

        self._stack.addWidget(self._library_view)  # 0
        self._stack.addWidget(self._search_view)   # 1
        self._stack.addWidget(self._download_view) # 2
        self._stack.addWidget(self._settings_page)  # 3

        content_layout.addWidget(self._stack, stretch=1)
        main_layout.addWidget(content, stretch=1)

        # Bottom Player Bar Controller layout panel
        self._player_bar = PlayerBar(self._engine)
        main_layout.addWidget(self._player_bar)

        # Refresh all structural dictionary strings natively
        self.retranslate_ui()

        # Default to initial track list view
        self._nav_btns["library"].setChecked(True)
        self._stack.setCurrentIndex(0)

    def _make_nav_btn(self, text):
        btn = QPushButton(text)
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
        return btn

    def retranslate_ui(self):
        """Refreshes language tracking text targets across active window frames."""
        self._library_btn.setText(f"🎵  {LANG.get('your_playlist')}")
        self._search_btn.setText(f"🔍  {LANG.get('explore')}")
        self._downloads_btn.setText(f"⬇  {LANG.get('download')}")
        self.settings_btn.setText(f"⚙  {LANG.get('settings')}")

    def _connect_signals(self):
        self._nav_btns["library"].clicked.connect(lambda: self._switch_view(0))
        self._nav_btns["search"].clicked.connect(lambda: self._switch_view(1))
        self._nav_btns["downloads"].clicked.connect(lambda: self._switch_view(2))
        self.settings_btn.clicked.connect(lambda: self._switch_view(3))

        self._library_view.play_song_requested.connect(self._play_song)
        self._download_view.song_ready.connect(self._library_view.refresh)

        # Connect settings slots to trigger UI modifications
        self._settings_page.language_changed.connect(self._on_language_changed)
        self._settings_page.theme_changed.connect(self._on_theme_changed)

    def _switch_view(self, index):
        self._stack.setCurrentIndex(index)
        names = ["library", "search", "downloads", "settings"]
        for key, btn in self._nav_btns.items():
            btn.setChecked(key == names[index])

    def _on_language_changed(self, lang_code):
        """Triggers when choice box inside settings shifts state."""
        print(f"changing lang : {lang_code}")
        Config.set("lang", lang_code)        
        # Reload translation files and rebuild views
        LANG.load_settings()
        self.retranslate_ui()
        
        # If your views have custom update/refresh hooks, call them here:
        # self._library_view.refresh()

    def _on_theme_changed(self, theme_value):
        """Swaps standard styles on the central window frame architecture."""
        Config.set("theme", theme_value)
        if theme_value == "dark":
            self.setStyleSheet(DARK_STYLE)
        else:
            self.setStyleSheet(LIGHT_STYLE)

    def _play_song(self, song, restart=False):
        songs = self._library_mgr.get_all_songs()
        self._engine.set_playlist(songs)
        for i, s in enumerate(songs):
            if s["id"] == song["id"]:
                self._engine.set_playlist(songs, start_index=i, restart=restart)
                break
        else:
            self._engine.play_song(song, restart=restart)

    def _restore_volume(self):
        vol = Config.get("volume", 80)
        self._engine.volume = vol

    def closeEvent(self, event):
        Config.set("volume", self._engine.volume)
        self._player_bar.running = False
        self._engine.cleanup()
        super().closeEvent(event)

    def _setup_shortcuts(self):
        self.shortcut_space = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        self.shortcut_space.activated.connect(self._engine.toggle_play_pause)

        self.shortcut_up = QShortcut(QKeySequence(Qt.Key.Key_Up), self)
        self.shortcut_up.activated.connect(lambda: self._engine.set_volume(min(100, self._engine.volume + 5)))

        self.shortcut_down = QShortcut(QKeySequence(Qt.Key.Key_Down), self)
        self.shortcut_down.activated.connect(lambda: self._engine.set_volume(max(0, self._engine.volume - 5)))

        self.shortcut_left = QShortcut(QKeySequence(Qt.Key.Key_Left), self)
        self.shortcut_left.activated.connect(lambda: self._engine.step_position(-5))

        self.shortcut_right = QShortcut(QKeySequence(Qt.Key.Key_Right), self)
        self.shortcut_right.activated.connect(lambda: self._engine.step_position(5))