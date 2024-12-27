MAIN_STYLE = """
QMainWindow {
    background-color: #2b2b2b;
    color: #ffffff;
}

QTabWidget::pane {
    border: 1px solid #3a3a3a;
    background: #2b2b2b;
}

QTabWidget::tab-bar {
    left: 5px;
}

QTabBar::tab {
    background: #353535;
    color: #ffffff;
    padding: 8px 20px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background: #0d87d4;
}

QTabBar::tab:hover {
    background: #454545;
}

QPushButton {
    background-color: #0d87d4;
    color: white;
    border: none;
    padding: 8px 15px;
    border-radius: 4px;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #0a6ca8;
}

QPushButton:pressed {
    background-color: #085a8c;
}

QLabel {
    color: #ffffff;
    font-size: 14px;
}

QSwitch {
    background-color: #353535;
    border-radius: 10px;
    padding: 2px;
}

QLineEdit {
    background-color: #353535;
    border: 1px solid #3a3a3a;
    border-radius: 4px;
    padding: 5px;
    color: white;
}

QStatusBar {
    background-color: #353535;
    color: white;
}

QMenuBar {
    background-color: #353535;
    color: white;
}

QMenuBar::item {
    padding: 5px 10px;
    background-color: transparent;
}

QMenuBar::item:selected {
    background-color: #0d87d4;
}

QMenu {
    background-color: #353535;
    color: white;
    border: 1px solid #3a3a3a;
}

QMenu::item:selected {
    background-color: #0d87d4;
}
"""

TITLE_BAR_STYLE = """
QWidget#TitleBar {
    background-color: #353535;
}

QPushButton#MinimizeButton {
    background-color: transparent;
    border: none;
    padding: 5px;
    border-radius: 0;
}

QPushButton#MaximizeButton {
    background-color: transparent;
    border: none;
    padding: 5px;
    border-radius: 0;
}

QPushButton#CloseButton {
    background-color: transparent;
    border: none;
    padding: 5px;
    border-radius: 0;
}

QPushButton#MinimizeButton:hover {
    background-color: #404040;
}

QPushButton#MaximizeButton:hover {
    background-color: #404040;
}

QPushButton#CloseButton:hover {
    background-color: #e81123;
}
"""
