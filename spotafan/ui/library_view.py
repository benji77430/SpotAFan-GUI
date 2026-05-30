import os
from spotafan.config import Config
from spotafan.player.engine import PlayerEngine
from spotafan.Lang import LANG

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QMenu, QFrame, QAbstractItemView, QMessageBox,QStyledItemDelegate,QStyle,
)

class NoFocusDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Safely remove ONLY the focus state using a bitwise AND + NOT mask
        if option.state & QStyle.StateFlag.State_HasFocus:
            option.state &= ~QStyle.StateFlag.State_HasFocus
        super().paint(painter, option, index)

class LibraryView(QFrame):
    play_song_requested = Signal(dict)
    play_all_requested = Signal()

    def __init__(self, library_manager, database, parent=None):
        super().__init__(parent)
        Config.load_settings()
        LANG.load_settings()

        self._library = library_manager
        self._db = database
        self._songs = []
        self.setObjectName("card")
        self._setup_ui()
        self._connect_signals()
        self.refresh()


    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title = QLabel(LANG.get("your_playlist"))
        title.setObjectName("header")
        header.addWidget(title)
        header.addStretch()

        self._count_label = QLabel(f"0 {LANG.get("songs")}")
        self._count_label.setObjectName("subtitle")
        header.addWidget(self._count_label)
        layout.addLayout(header)

        # Search bar
        search_row = QHBoxLayout()
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(LANG.get("search_in_librairy"))
        self._search_input.setClearButtonEnabled(True)
        search_row.addWidget(self._search_input, stretch=1)

        self._import_btn = QPushButton(LANG.get("import"))
        self._import_btn.setStyleSheet(
            "background-color: transparent; border: 1px solid #535353; "
            "border-radius: 20px; padding: 8px 20px; color: #ffffff;"
        )
        search_row.addWidget(self._import_btn)

        self._refresh_btn = QPushButton("🔄")
        self._refresh_btn.setObjectName("iconic")
        self._refresh_btn.setToolTip("Refresh library")
        search_row.addWidget(self._refresh_btn)
        layout.addLayout(search_row)

        # Table
        self._table = QTableWidget()
        self._table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["", LANG.get("title"), LANG.get("artist"), LANG.get("duration")])
        self._table.setColumnWidth(0, 40)
        self._table.horizontalHeader().setStretchLastSection(False)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(3, 80)
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setShowGrid(False)
        self._table.setAlternatingRowColors(False)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.setMinimumHeight(300)

        layout.addWidget(self._table)

    def _connect_signals(self):
        self._library.library_changed.connect(self.refresh)
        self._search_input.textChanged.connect(self._on_search)
        self._refresh_btn.clicked.connect(self.refresh)
        self._import_btn.clicked.connect(self._import_file)
        self._table.itemDoubleClicked.connect(self._on_item_double_clicked)
        self._table.customContextMenuRequested.connect(self._show_context_menu)
        self._table.itemClicked.connect(self._show_context_menu)

    def refresh(self):
        self._songs = self._library.get_all_songs()
        self._populate_table(self._songs)

    def _on_search(self, text):
        if text:
            self._songs = self._library.search(text)
        else:
            self._songs = self._library.get_all_songs()
        self._populate_table(self._songs)

    def _populate_table(self, songs):
        self._table.setRowCount(len(songs))
        for row, song in enumerate(songs):
            play = QTableWidgetItem("▶")
            play.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 0, play)

            title_item = QTableWidgetItem(song.get("title", LANG.get("unknown_track")))
            title_item.setData(Qt.ItemDataRole.UserRole, song["id"])
            self._table.setItem(row, 1, title_item)

            artist_item = QTableWidgetItem(song.get("artist", LANG.get("unknown_artist")))
            self._table.setItem(row, 2, artist_item)

            dur = song.get("duration", 0)
            dur_text = self._format_time(dur) if dur else "--:--"
            dur_item = QTableWidgetItem(dur_text)
            dur_item.setTextAlignment(Qt.AlignmentFlag.AlignRight |
                                       Qt.AlignmentFlag.AlignVCenter)
            self._table.setItem(row, 3, dur_item)

            self._table.setRowHeight(row, 48)

        self._count_label.setText(f"{len(songs)}  {LANG.get("songs")}")

    def _on_item_double_clicked(self, item):
        row = item.row()
        print(f"row : {row}")
        if 0 <= row < len(self._songs):
            self.play_song_requested.emit(self._songs[row])

    def _show_context_menu(self, pos):
        item = self._table.itemAt(pos)
        if not item:
            return
        row = item.row()
        if row < 0 or row >= len(self._songs):
            return
        song = self._songs[row]
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: #282828; color: #ffffff;
                    border: 1px solid #535353; padding: 4px; }
            QMenu::item { padding: 8px 24px; border-radius: 4px; }
            QMenu::item:selected { background-color: #1db954; }
        """)

        play_act = menu.addAction(f"▶ {LANG.get("play")}")
        play_next = menu.addAction(f"⏭ {LANG.get("play_next")}")
        menu.addSeparator()
        delete_act = menu.addAction(f"🗑 {LANG.get("delete_from_lib")}")

        action = menu.exec(self._table.mapToGlobal(pos))

        if action == play_act:
            self.play_song_requested.emit(song)
        elif action == play_next:
            self.play_song_requested.emit(song)
        elif action == delete_act:
            self._delete_song(song)

    def _delete_song(self, song):
        reply = QMessageBox.question(
            self, LANG.get("delete_song"),
            f'{LANG.get("delete")} "{song.get("title")}" {LANG.get("from_lib")}'
            f"\n{LANG.get("will_also_be_removed_from_disk")}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._library.delete_song(song)

    def _import_file(self):
        from PySide6.QtWidgets import QFileDialog
        files, _ = QFileDialog.getOpenFileNames(
            self, LANG.get("import"), "",
            "Audio Files (*.mp3 *.flac *.ogg *.wav *.m4a *.wma *.webm);;All Files (*)",
        )
        for fp in files:
            self._library.import_local_file(fp)

    @staticmethod
    def _format_time(seconds):
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m}:{s:02d}"
