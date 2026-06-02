from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QStackedWidget,
    QLabel, QComboBox, QPushButton, QSlider, QCheckBox, QFrame,
    QFileDialog, QMessageBox, QListWidgetItem,QLineEdit
)
from PySide6.QtGui import QFont

from spotafan.config import Config
from spotafan.Lang import LANG

class SettingsPage(QWidget):
    # Signals to notify your main application when a setting changes
    language_changed = Signal(str)  # Emits e.g., 'en', 'fr', 'es'
    theme_changed = Signal(str)     # Emits e.g., 'Dark', 'Light', 'AMOLED'

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settings_page")
        self.resize(750, 500)
        Config.load_settings()
        LANG.load_settings()
        
        # Apply clean dark dashboard styling
        self.setStyleSheet("""
            QWidget#settings_page {
                background-color: #121212;
            }
            QListWidget {
                background-color: #181818;
                border: none;
                border-right: 1px solid #282828;
                color: #b3b3b3;
                font-size: 13px;
                padding: 10px;
            }
            QListWidget::item {
                padding: 10px 15px;
                border-radius: 4px;
                margin-bottom: 4px;
            }
            QListWidget::item:hover {
                background-color: #282828;
                color: #ffffff;
            }
            QListWidget::item:selected {
                background-color: #282828;
                color: #1db954; /* Spotify green accent */
                font-weight: bold;
            }
            QLabel {
                color: #ffffff;
            }
            QLabel#section_title {
                font-size: 22px;
                font-weight: bold;
                margin-bottom: 15px;
            }
            QLabel#setting_label {
                font-size: 14px;
                font-weight: semi-bold;
            }
            QLabel#setting_desc {
                color: #a7a7a7;
                font-size: 11px;
            }
            QComboBox {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QPushButton {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #3e3e3e;
                border-color: #ffffff;
            }
            QPushButton#danger_btn {
                background-color: #b72121;
                border: none;
            }
            QPushButton#danger_btn:hover {
                background-color: #e93939;
            }
            QFrame#separator {
                background-color: #282828;
                max-height: 1px;
            }
        """)

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Left Sidebar Navigation
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(180)
        self.sidebar.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.sidebar.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Add navigation items
        items = [LANG.get("language"), LANG.get("appearence"), LANG.get("downloads_and_storage")]
        for item_text in items:
            item = QListWidgetItem(item_text)
            self.sidebar.addItem(item)
            
        main_layout.addWidget(self.sidebar)

        # 2. Right Content Area (Stacked view for swapping frames)
        self.pages_container = QStackedWidget()
        self.pages_container.setStyleSheet("padding: 24px;")
        
        # Build individual view pages
        self._page_language = self._create_language_page()
        self._page_appearance = self._create_appearance_page()
        self._page_storage = self._create_storage_page()
        
        self.pages_container.addWidget(self._page_language)
        self.pages_container.addWidget(self._page_appearance)
        self.pages_container.addWidget(self._page_storage)
        
        main_layout.addWidget(self.pages_container)

        # Connect Sidebar selection jumps
        self.sidebar.currentRowChanged.connect(self.pages_container.setCurrentIndex)
        self.sidebar.setCurrentRow(0)

    def _create_row_separator(self):
        sep = QFrame()
        sep.setObjectName("separator")
        return sep

    # --- INDIVIDUAL SUB PANELS ---

    def _create_language_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(16)

        title = QLabel(LANG.get("language_preferences"))
        title.setObjectName("section_title")
        layout.addWidget(title)

        # Combo choice row
        row = QHBoxLayout()
        info_vbox = QVBoxLayout()
        lbl = QLabel(LANG.get("app_language"))
        lbl.setObjectName("setting_label")
        desc = QLabel(LANG.get("app_lang_desc"))
        desc.setObjectName("setting_desc")
        info_vbox.addWidget(lbl)
        info_vbox.addWidget(desc)
        
        self.lang_box = QComboBox()
        # Pair display names with code dictionary variables
        for key, content in LANG.DEFAULT_LANGS.items():
            self.lang_box.addItem(content, key)
            
        # 2. Automatically select the one currently saved in your config
        current_lang = Config.get("lang")
        index = self.lang_box.findData(current_lang)
        if index != -1:
            self.lang_box.setCurrentIndex(index)
        
        
        row.addLayout(info_vbox)
        row.addStretch()
        row.addWidget(self.lang_box)
        layout.addLayout(row)
        
        # Signal emission connecting to your global LANG class
        self.lang_box.currentIndexChanged.connect(
            lambda: self.language_changed.emit(self.lang_box.currentData())
        )
        return page

    def _create_appearance_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(16)

        title = QLabel(LANG.get("themes"))
        title.setObjectName("section_title")
        layout.addWidget(title)

        # Theme Chooser row
        row = QHBoxLayout()
        info_vbox = QHBoxLayout()
        lbl = QLabel(LANG.get("color_theme"))
        lbl.setObjectName("setting_label")
        desc = QLabel(LANG.get("choose_theme"))
        desc.setObjectName("setting_desc")
        info_vbox.addWidget(lbl)
        info_vbox.addWidget(desc)

        self.theme_box = QComboBox()
        self.theme_box.addItems(Config.THEMES)
        
        row.addLayout(info_vbox)
        row.addStretch()
        row.addWidget(self.theme_box)
        layout.addLayout(row)
        
        self.theme_box.currentTextChanged.connect(self.theme_changed.emit)

        return page

    def _create_storage_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(13)

        title = QLabel(LANG.get("downloads_and_storage"))
        title.setObjectName("section_title")
        layout.addWidget(title)

        # Download Directory row
        row1 = QHBoxLayout()
        info_vbox = QVBoxLayout()
        lbl1 = QLabel(LANG.get("download_location"))
        lbl1.setObjectName("setting_label")
        self.path_lbl = QLabel(Config.get("download_directory"))
        self.path_lbl.setObjectName("setting_desc")
        info_vbox.addWidget(lbl1)
        info_vbox.addWidget(self.path_lbl)

        change_path_btn = QPushButton(LANG.get("change_folder"))
        change_path_btn.clicked.connect(self._select_download_dir)
        
        row1.addLayout(info_vbox)
        row1.addStretch()
        row1.addWidget(change_path_btn)


        # Search query max_results row
        row2 = QVBoxLayout()
        info_vbox2 = QHBoxLayout()
        lbl2 = QLabel(LANG.get("max_results"))
        lbl2.setObjectName("setting_label2")
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(LANG.get("enter_max_results"))
        self.current_max_results = QLabel(str(Config.get("max_results",LANG.get("settings_not_defined"))))
        self.current_max_results.setObjectName("setting_desc")
        info_vbox2.addWidget(lbl2)
        info_vbox2.addWidget(self._search_input,stretch=3)
        
        row2.addLayout(info_vbox2)
        row2.addWidget(self.current_max_results)
        
        self._search_input.returnPressed.connect(lambda:Config.set("max_results",int(self._search_input.text().strip())))

        layout.addLayout(row1)
        layout.addLayout(row2)
        layout.addWidget(self._create_row_separator())

        return page

    def _select_download_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, LANG.get("select_destination"))
        if dir_path:
            self.path_lbl.setText(dir_path)
            Config.set("download_directory",dir_path)