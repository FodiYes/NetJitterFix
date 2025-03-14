from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication


class NeonTheme:
    DARK_BG = "#121212"
    DARKER_BG = "#0A0A0A"
    NEON_BLUE = "#00FFFF"
    NEON_PURPLE = "#AD00AD"
    NEON_PINK = "#FF00FF"
    NEON_GREEN = "#39FF14"
    TEXT_COLOR = "#FFFFFF"
    TEXT_SECONDARY = "#AAAAAA"
    
    @staticmethod
    def apply_theme(app: QApplication) -> None:
        palette = QPalette()
        
        palette.setColor(QPalette.ColorRole.Window, QColor(NeonTheme.DARK_BG))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(NeonTheme.TEXT_COLOR))
        palette.setColor(QPalette.ColorRole.Base, QColor(NeonTheme.DARKER_BG))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(NeonTheme.DARK_BG))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(NeonTheme.DARK_BG))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(NeonTheme.TEXT_COLOR))
        palette.setColor(QPalette.ColorRole.Text, QColor(NeonTheme.TEXT_COLOR))
        palette.setColor(QPalette.ColorRole.Button, QColor(NeonTheme.DARK_BG))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(NeonTheme.TEXT_COLOR))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(NeonTheme.NEON_GREEN))
        palette.setColor(QPalette.ColorRole.Link, QColor(NeonTheme.NEON_BLUE))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(NeonTheme.NEON_PURPLE))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(NeonTheme.TEXT_COLOR))
        
        app.setPalette(palette)
        
    @staticmethod
    def get_stylesheet() -> str:
        return f"""
        QWidget {{
            background-color: {NeonTheme.DARK_BG};
            color: {NeonTheme.TEXT_COLOR};
            font-family: 'Segoe UI', 'Arial';
            font-size: 10pt;
        }}
        
        QMainWindow, QDialog {{
            background-color: {NeonTheme.DARK_BG};
        }}
        
        QLabel {{
            color: {NeonTheme.TEXT_COLOR};
        }}
        
        QLabel#titleLabel {{
            font-size: 18pt;
            font-weight: bold;
            color: {NeonTheme.NEON_BLUE};
        }}
        
        QLabel#resultLabel {{
            font-size: 14pt;
            font-weight: bold;
            color: {NeonTheme.NEON_GREEN};
        }}
        
        QPushButton {{
            background-color: {NeonTheme.DARKER_BG};
            color: {NeonTheme.TEXT_COLOR};
            border: 2px solid {NeonTheme.NEON_BLUE};
            border-radius: 5px;
            padding: 8px 16px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: {NeonTheme.NEON_BLUE};
            color: {NeonTheme.DARKER_BG};
        }}
        
        QPushButton:pressed {{
            background-color: {NeonTheme.NEON_PURPLE};
            border: 2px solid {NeonTheme.NEON_PURPLE};
        }}
        
        QPushButton#fixButton {{
            background-color: {NeonTheme.DARKER_BG};
            color: {NeonTheme.TEXT_COLOR};
            border: 2px solid {NeonTheme.NEON_GREEN};
        }}
        
        QPushButton#fixButton:hover {{
            background-color: {NeonTheme.NEON_GREEN};
            color: {NeonTheme.DARKER_BG};
        }}
        
        QPushButton#fixButton:pressed {{
            background-color: {NeonTheme.NEON_PURPLE};
            border: 2px solid {NeonTheme.NEON_PURPLE};
        }}
        
        QProgressBar {{
            border: 2px solid {NeonTheme.NEON_PURPLE};
            border-radius: 5px;
            text-align: center;
            color: {NeonTheme.TEXT_COLOR};
            background-color: {NeonTheme.DARKER_BG};
        }}
        
        QProgressBar::chunk {{
            background-color: {NeonTheme.NEON_BLUE};
            width: 10px;
            margin: 0.5px;
        }}
        
        QCheckBox {{
            color: {NeonTheme.TEXT_COLOR};
            spacing: 5px;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
        }}
        
        QCheckBox::indicator:unchecked {{
            border: 2px solid {NeonTheme.NEON_BLUE};
            background-color: {NeonTheme.DARKER_BG};
        }}
        
        QCheckBox::indicator:checked {{
            border: 2px solid {NeonTheme.NEON_GREEN};
            background-color: {NeonTheme.NEON_GREEN};
        }}
        
        QComboBox {{
            border: 2px solid {NeonTheme.NEON_BLUE};
            border-radius: 5px;
            padding: 5px;
            background-color: {NeonTheme.DARKER_BG};
            color: {NeonTheme.TEXT_COLOR};
        }}
        
        QComboBox:hover {{
            border: 2px solid {NeonTheme.NEON_PURPLE};
        }}
        
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: right;
            width: 15px;
            border-left-width: 1px;
            border-left-color: {NeonTheme.NEON_BLUE};
            border-left-style: solid;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {NeonTheme.DARKER_BG};
            color: {NeonTheme.TEXT_COLOR};
            selection-background-color: {NeonTheme.NEON_PURPLE};
            selection-color: {NeonTheme.TEXT_COLOR};
        }}
        
        QGroupBox {{
            border: 2px solid {NeonTheme.NEON_BLUE};
            border-radius: 5px;
            margin-top: 20px;
            padding-top: 15px;
            color: {NeonTheme.NEON_BLUE};
            font-weight: bold;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 5px;
        }}
        
        QTabWidget::pane {{
            border: 2px solid {NeonTheme.NEON_BLUE};
            border-radius: 5px;
        }}
        
        QTabBar::tab {{
            background-color: {NeonTheme.DARKER_BG};
            color: {NeonTheme.TEXT_COLOR};
            border: 2px solid {NeonTheme.NEON_BLUE};
            border-bottom: none;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
            padding: 8px 12px;
            margin-right: 2px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {NeonTheme.NEON_BLUE};
            color: {NeonTheme.DARKER_BG};
            font-weight: bold;
        }}
        
        QTabBar::tab:!selected:hover {{
            background-color: {NeonTheme.DARKER_BG};
            border: 2px solid {NeonTheme.NEON_PURPLE};
            border-bottom: none;
        }}
        
        QScrollBar:vertical {{
            background: {NeonTheme.DARKER_BG};
            width: 12px;
            margin: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background: {NeonTheme.NEON_BLUE};
            min-height: 20px;
            border-radius: 3px;
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            background: {NeonTheme.DARKER_BG};
            height: 12px;
            margin: 0px;
        }}
        
        QScrollBar::handle:horizontal {{
            background: {NeonTheme.NEON_BLUE};
            min-width: 20px;
            border-radius: 3px;
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        """
