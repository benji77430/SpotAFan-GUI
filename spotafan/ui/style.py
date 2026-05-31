DARK_STYLE = """
QMainWindow, QWidget {
    background-color: #121212;
    color: #ffffff;
    font-family: 'Segoe UI', 'SF Pro Display', 'Ubuntu', sans-serif;
    outline: none;
}

QPushButton {
    background-color: #1db954;
    color: #ffffff;
    border: none;
    border-radius: 20px;
    padding: 8px 24px;
    font-size: 13px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #1ed760;
}
QPushButton:pressed {
    background-color: #169c46;
}
QPushButton:disabled {
    background-color: #535353;
    color: #b3b3b3;
}

QPushButton#iconic {
    background-color: transparent;
    border-radius: 4px;
    padding: 6px 10px;
}
QPushButton#iconic:hover {
    background-color: #282828;
}

QLineEdit, QTextEdit {
    background-color: #282828;
    color: #ffffff;
    border: 1px solid #535353;
    border-radius: 20px;
    padding: 8px 16px;
    font-size: 14px;
}
QLineEdit:focus, QTextEdit:focus {
    border: 2px solid #1db954;
}

QListWidget, QTableWidget, QTreeWidget {
    background-color: #121212;
    color: #ffffff;
    border: none;
    outline: none;
    font-size: 14px;
    paint-alternating-row-colors-for-empty-area: true;
}
QListWidget:focus, QTableWidget:focus, QTreeWidget:focus {
    outline: none;
    border: none;
}
QListWidget::item, QTableWidget::item, QTreeWidget::item {
    padding: 8px 12px;
    outline: none;
}
QListWidget::item:selected, QTableWidget::item:selected, QTreeWidget::item:selected {
    background-color: #282828;
}
QListWidget::item:hover, QTableWidget::item:hover, QTreeWidget::item:hover {
    background-color: #1e1e1e;
}

QHeaderView::section {
    background-color: #121212;
    color: #b3b3b3;
    font-weight: bold;
    border: none;
    border-bottom: 1px solid #282828;
    padding: 8px;
}

QScrollBar:vertical {
    background-color: #121212;
    width: 8px;
    border: none;
}
QScrollBar::handle:vertical {
    background-color: #535353;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background-color: #7a7a7a;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: #121212;
    height: 8px;
    border: none;
}
QScrollBar::handle:horizontal {
    background-color: #535353;
    border-radius: 4px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover {
    background-color: #7a7a7a;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

QSlider {
    background: transparent;
}

QSlider::groove:horizontal {
    background: #535353;
    height: 4px;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #ffffff;
    width: 12px;
    height: 12px;
    margin: -4px 0;
    border-radius: 6px;
}
QSlider::handle:horizontal:hover {
    background: #1db954;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::sub-page:horizontal {
    background: #1db954;
    border-radius: 2px;
}

QSlider::groove:vertical {
    background: #535353;
    width: 4px;
    border-radius: 2px;
}
QSlider::handle:vertical {
    background: #ffffff;
    width: 12px;
    height: 12px;
    margin: 0 -4px;
    border-radius: 6px;
}
QSlider::sub-page:vertical {
    background: #1db954;
    border-radius: 2px;
}

QLabel#title {
    font-size: 16px;
    font-weight: bold;
    color: #ffffff;
}
QLabel#subtitle {
    font-size: 13px;
    color: #b3b3b3;
}
QLabel#header {
    font-size: 24px;
    font-weight: bold;
    color: #ffffff;
}
QLabel#section {
    font-size: 18px;
    font-weight: bold;
    color: #ffffff;
    padding: 16px 0 8px 0;
}

QProgressBar {
    background-color: #282828;
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
    font-size: 10px;
    color: transparent;
}
QProgressBar::chunk {
    background-color: #1db954;
    border-radius: 4px;
}

QTabWidget::pane {
    border: none;
    background-color: #121212;
}
QTabBar::tab {
    background-color: transparent;
    color: #b3b3b3;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: bold;
    border: none;
    border-bottom: 2px solid transparent;
}
QTabBar::tab:selected {
    color: #ffffff;
    border-bottom: 2px solid #1db954;
}
QTabBar::tab:hover {
    color: #ffffff;
}

QSplitter::handle {
    background-color: #282828;
    width: 1px;
}

QFrame#sidebar {
    background-color: #000000;
    border-right: 1px solid #282828;
}
QFrame#card {
    background-color: #181818;
    border-radius: 8px;
    padding: 16px;
}
QFrame#card:hover {
    background-color: #282828;
}
"""

LIGHT_STYLE = """
QMainWindow, QWidget {
    background-color: #f2f2f7; /* Soft gray app background so widgets pop out */
    color: #1c1c1e;
    font-family: 'Segoe UI', 'SF Pro Display', 'Ubuntu', sans-serif;
    outline: none;
}

QPushButton {
    background-color: #1db954;
    color: #ffffff;
    border: none;
    border-radius: 20px;
    padding: 8px 24px;
    font-size: 13px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #1aa34a;
}
QPushButton:pressed {
    background-color: #147d39;
}
QPushButton:disabled {
    background-color: #e5e5ea;
    color: #aeaeae;
}

QPushButton#iconic {
    background-color: transparent;
    border-radius: 4px;
    padding: 6px 10px;
}
QPushButton#iconic:hover {
    background-color: #e5e5ea;
}

QLineEdit, QTextEdit {
    background-color: #ffffff; /* Stark contrast against the layout background */
    color: #1c1c1e;
    border: 1px solid #c7c7cc;
    border-radius: 20px;
    padding: 8px 16px;
    font-size: 14px;
}
QLineEdit:focus, QTextEdit:focus {
    border: 2px solid #1db954;
}

QListWidget, QTableWidget, QTreeWidget {
    background-color: #ffffff;
    color: #1c1c1e;
    border: 1px solid #d1d1d6;
    border-radius: 8px;
    outline: none;
    font-size: 14px;
    paint-alternating-row-colors-for-empty-area: true;
}
QListWidget:focus, QTableWidget:focus, QTreeWidget:focus {
    border: 1px solid #1db954;
}
QListWidget::item, QTableWidget::item, QTreeWidget::item {
    padding: 10px 12px;
    border-radius: 6px;
    outline: none;
}
QListWidget::item:selected, QTableWidget::item:selected, QTreeWidget::item:selected {
    background-color: #e5e5ea;
    color: #1c1c1e;
    font-weight: bold;
}
QListWidget::item:hover, QTableWidget::item:hover, QTreeWidget::item:hover {
    background-color: #f2f2f7;
}

QHeaderView::section {
    background-color: #f2f2f7;
    color: #48484a;
    font-weight: bold;
    border: none;
    border-bottom: 1px solid #d1d1d6;
    padding: 8px;
}

QScrollBar:vertical {
    background-color: #f2f2f7;
    width: 8px;
    border: none;
}
QScrollBar::handle:vertical {
    background-color: #c7c7cc;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background-color: #8e8e93;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: #f2f2f7;
    height: 8px;
    border: none;
}
QScrollBar::handle:horizontal {
    background-color: #c7c7cc;
    border-radius: 4px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover {
    background-color: #8e8e93;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

QSlider {
    background: transparent;
}
QSlider::groove:horizontal {
    background: #d1d1d6;
    height: 4px;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #ffffff;
    border: 1px solid #c7c7cc;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::handle:horizontal:hover {
    background: #1db954;
    border-color: #1db954;
}
QSlider::sub-page:horizontal {
    background: #1db954;
    border-radius: 2px;
}

QSlider::groove:vertical {
    background: #d1d1d6;
    width: 4px;
    border-radius: 2px;
}
QSlider::handle:vertical {
    background: #ffffff;
    border: 1px solid #c7c7cc;
    width: 14px;
    height: 14px;
    margin: 0 -5px;
    border-radius: 7px;
}
QSlider::sub-page:vertical {
    background: #1db954;
    border-radius: 2px;
}

QLabel#title {
    font-size: 16px;
    font-weight: bold;
    color: #1c1c1e;
}
QLabel#subtitle {
    font-size: 13px;
    color: #48484a;
}
QLabel#header {
    font-size: 24px;
    font-weight: bold;
    color: #1c1c1e;
}
QLabel#section {
    font-size: 18px;
    font-weight: bold;
    color: #1c1c1e;
    padding: 16px 0 8px 0;
}

QProgressBar {
    background-color: #d1d1d6;
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
    font-size: 10px;
    color: transparent;
}
QProgressBar::chunk {
    background-color: #1db954;
    border-radius: 4px;
}

QTabWidget::pane {
    border: 1px solid #d1d1d6;
    border-radius: 8px;
    background-color: #ffffff;
}
QTabBar::tab {
    background-color: transparent;
    color: #48484a;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: bold;
    border: none;
    border-bottom: 2px solid transparent;
}
QTabBar::tab:selected {
    color: #1db954;
    border-bottom: 2px solid #1db954;
}
QTabBar::tab:hover {
    color: #1c1c1e;
}

QSplitter::handle {
    background-color: #d1d1d6;
    width: 1px;
}

QFrame#sidebar {
    background-color: #e5e5ea; /* Darker than the body background for anchor effect */
    border-right: 1px solid #c7c7cc;
}
QFrame#card {
    background-color: #ffffff; /* Clean distinct card blocks */
    border: 1px solid #d1d1d6;
    border-radius: 8px;
    padding: 16px;
}
QFrame#card:hover {
    background-color: #fafafa;
    border-color: #c7c7cc;
}
"""