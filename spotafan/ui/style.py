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
    border: rgba(255, 255, 255, 0.5) 2px solid;
    border-radius: 4px;
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
    background-color: #ffffff;
    color: #000000;
    font-family: 'Segoe UI', 'SF Pro Display', 'Ubuntu', sans-serif;
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
QPushButton:disabled {
    background-color: #e0e0e0;
    color: #999999;
}

QPushButton#iconic {
    background-color: transparent;
    border-radius: 4px;
    padding: 6px 10px;
}
QPushButton#iconic:hover {
    background-color: #f0f0f0;
}

QLineEdit, QTextEdit {
    background-color: #f5f5f5;
    color: #000000;
    border: 1px solid #cccccc;
    border-radius: 20px;
    padding: 8px 16px;
    font-size: 14px;
}

QListWidget, QTableWidget, QTreeWidget {
    background-color: #ffffff;
    color: #000000;
    border: none;
    font-size: 14px;
}
QListWidget::item:selected, QTableWidget::item:selected, QTreeWidget::item:selected {
    background-color: #e8f5e9;
}
QListWidget::item:hover, QTableWidget::item:hover, QTreeWidget::item:hover {
    background-color: #f5f5f5;
}

QHeaderView::section {
    background-color: #ffffff;
    color: #666666;
    border: none;
    border-bottom: 1px solid #e0e0e0;
}

QScrollBar:vertical {
    background-color: #ffffff;
    width: 8px;
}
QScrollBar::handle:vertical {
    background-color: #cccccc;
    border-radius: 4px;
    min-height: 30px;
}

QSlider::groove:horizontal {
    background: #e0e0e0;
    height: 4px;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #1db954;
    width: 12px;
    height: 12px;
    margin: -4px 0;
    border-radius: 6px;
}
QSlider::sub-page:horizontal {
    background: #1db954;
    border-radius: 2px;
}

QFrame#sidebar {
    background-color: #fafafa;
    border-right: 1px solid #e0e0e0;
}
QFrame#card {
    background-color: #f8f8f8;
    border-radius: 8px;
    padding: 16px;
}
QFrame#card:hover {
    background-color: #f0f0f0;
}

QLabel#header {
    font-size: 24px;
    font-weight: bold;
}
QLabel#section {
    font-size: 18px;
    font-weight: bold;
    padding: 16px 0 8px 0;
}
"""
