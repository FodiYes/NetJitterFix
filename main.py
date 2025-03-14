import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from gui.main_window import MainWindow
from gui.theme import NeonTheme


def main():
    app = QApplication(sys.argv)
    
    NeonTheme.apply_theme(app)
    app.setStyleSheet(NeonTheme.get_stylesheet())
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
