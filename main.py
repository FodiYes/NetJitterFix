import sys
import asyncio
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QTabWidget, QStatusBar, QFrame)
from PyQt5.QtCore import Qt, QPoint
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from qasync import QEventLoop

from utils.network_optimizer import NetworkOptimizer
from utils.network_tester import NetworkTester
from utils.styles import MAIN_STYLE, TITLE_BAR_STYLE

class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("TitleBar")
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.title_label = QLabel("NetJitterFix")
        self.title_label.setStyleSheet("color: white; font-size: 14px; padding: 5px;")
        
        self.minimize_btn = QPushButton("─")
        self.maximize_btn = QPushButton("□")
        self.close_btn = QPushButton("✕")
        
        for btn in [self.minimize_btn, self.maximize_btn, self.close_btn]:
            btn.setFixedSize(45, 30)
            btn.setObjectName(btn.text() + "Button")
        
        self.minimize_btn.setObjectName("MinimizeButton")
        self.maximize_btn.setObjectName("MaximizeButton")
        self.close_btn.setObjectName("CloseButton")
        
        self.layout.addWidget(self.title_label)
        self.layout.addStretch()
        self.layout.addWidget(self.minimize_btn)
        self.layout.addWidget(self.maximize_btn)
        self.layout.addWidget(self.close_btn)
        
        self.minimize_btn.clicked.connect(self.parent.showMinimized)
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        self.close_btn.clicked.connect(self.parent.close)
        
        self.setStyleSheet(TITLE_BAR_STYLE)
        
    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent.drag_position = event.globalPos() - self.parent.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.parent.move(event.globalPos() - self.parent.drag_position)
            event.accept()

class ToggleSwitch(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 25)
        self.is_checked = False
        self.callback = None
        
    def paintEvent(self, event):
        from PyQt5.QtGui import QPainter, QColor, QPen
        from PyQt5.QtCore import QRect
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if self.is_checked:
            background_color = QColor(52, 152, 219)
        else:
            background_color = QColor(189, 195, 199)
            
        painter.setPen(Qt.NoPen)
        painter.setBrush(background_color)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 12, 12)
        
        knob_color = QColor(255, 255, 255)
        painter.setBrush(knob_color)
        if self.is_checked:
            knob_x = self.width() - 23
        else:
            knob_x = 3
        painter.drawEllipse(knob_x, 3, 19, 19)
        
    def mousePressEvent(self, event):
        self.is_checked = not self.is_checked
        self.update()
        if self.callback:
            self.callback(self.is_checked)
            
    def setChecked(self, checked):
        self.is_checked = checked
        self.update()
        if self.callback:
            self.callback(self.is_checked)
            
    def isChecked(self):
        return self.is_checked
    
    def stateChanged(self, callback):
        self.callback = callback

class OptimizationWidget(QWidget):
    def __init__(self, title, optimizer_func, restore_func, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        
        self.label = QLabel(title)
        self.toggle = ToggleSwitch()
        self.optimizer_func = optimizer_func
        self.restore_func = restore_func
        
        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.toggle)
        
        self.setLayout(layout)
        self.toggle.stateChanged(self.handle_toggle)
        
    def handle_toggle(self, checked):
        if checked:
            asyncio.create_task(self.apply_optimization())
        else:
            asyncio.create_task(self.restore_settings())
            
    def find_main_window(self):
        parent = self.parent()
        while parent is not None:
            if isinstance(parent, MainWindow):
                return parent
            parent = parent.parent()
        return None
            
    async def apply_optimization(self):
        try:
            main_window = self.find_main_window()
            if main_window:
                main_window.status_label.setText(f"Applying {self.label.text()}...")
            await self.optimizer_func()
            if main_window:
                main_window.status_label.setText(f"Applied {self.label.text()}")
        except Exception as e:
            if main_window:
                main_window.status_label.setText(f"Error: {str(e)}")
            
    async def restore_settings(self):
        try:
            main_window = self.find_main_window()
            if main_window:
                main_window.status_label.setText(f"Restoring settings for {self.label.text()}...")
            await self.restore_func()
            if main_window:
                main_window.status_label.setText(f"Restored original settings for {self.label.text()}")
        except Exception as e:
            if main_window:
                main_window.status_label.setText(f"Error: {str(e)}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NetJitterFix")
        self.setMinimumSize(900, 600)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.drag_position = None
        
        self.network_optimizer = NetworkOptimizer()
        self.network_tester = NetworkTester()
        
        self.status_label = QLabel("Ready")
        
        self.setup_ui()
        self.setStyleSheet(MAIN_STYLE)
        
    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        tabs = QTabWidget()
        content_layout.addWidget(tabs)
        
        tabs.addTab(self.create_optimization_tab(), "Optimization")
        tabs.addTab(self.create_testing_tab(), "Testing")
        tabs.addTab(self.create_settings_tab(), "Settings")
        
        main_layout.addWidget(content_widget)
        
        self.statusBar().addWidget(self.status_label)

    def create_optimization_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        mtu_widget = OptimizationWidget("MTU Optimization", 
                                      self.network_optimizer.optimize_mtu,
                                      self.network_optimizer.restore_mtu)
        tcp_widget = OptimizationWidget("TCP/UDP Optimization", 
                                      self.network_optimizer.optimize_tcp_udp,
                                      self.network_optimizer.restore_tcp_udp)
        buffer_widget = OptimizationWidget("Buffer Management", 
                                         self.network_optimizer.manage_buffer,
                                         self.network_optimizer.restore_buffer)
        
        layout.addWidget(mtu_widget)
        layout.addWidget(tcp_widget)
        layout.addWidget(buffer_widget)
        layout.addStretch()
        
        return tab
        
    def create_testing_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        test_before_btn = QPushButton("Run Pre-optimization Test")
        test_after_btn = QPushButton("Run Post-optimization Test")
        
        self.progress_label = QLabel("")
        
        test_before_btn.clicked.connect(lambda: asyncio.create_task(self.run_pre_test()))
        test_after_btn.clicked.connect(lambda: asyncio.create_task(self.run_post_test()))
        
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        
        layout.addWidget(test_before_btn)
        layout.addWidget(test_after_btn)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.canvas)
        
        return tab
        
    def create_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        settings_label = QLabel("Settings will be implemented here")
        layout.addWidget(settings_label)
        
        return tab

    async def run_pre_test(self):
        self.status_label.setText("Running pre-optimization test...")
        self.progress_label.setText("Testing packet loss...")
        try:
            results = await self.network_tester.run_pre_test()
            self.update_results_graph()
            self.status_label.setText("Pre-optimization test completed")
            self.progress_label.setText("")
        except Exception as e:
            self.status_label.setText(f"Error in pre-optimization test: {str(e)}")
            self.progress_label.setText("Test failed")
            
    async def run_post_test(self):
        self.status_label.setText("Running post-optimization test...")
        self.progress_label.setText("Testing packet loss...")
        try:
            results = await self.network_tester.run_post_test()
            self.update_results_graph()
            self.status_label.setText("Post-optimization test completed")
            self.progress_label.setText("")
        except Exception as e:
            self.status_label.setText(f"Error in post-optimization test: {str(e)}")
            self.progress_label.setText("Test failed")
            
    def update_results_graph(self):
        self.figure.clear()
        
        pre_results = self.network_tester.pre_test_results
        post_results = self.network_tester.post_test_results
        
        if not pre_results or not post_results:
            return
            
        ax = self.figure.add_subplot(111)
        
        metrics = list(pre_results.keys())
        pre_values = [pre_results[m] for m in metrics]
        post_values = [post_results[m] for m in metrics]
        
        x = range(len(metrics))
        width = 0.35
        
        ax.bar([i - width/2 for i in x], pre_values, width, label='Pre-optimization')
        ax.bar([i + width/2 for i in x], post_values, width, label='Post-optimization')
        
        ax.set_ylabel('Value')
        ax.set_title('Network Performance Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(metrics)
        ax.legend()
        
        self.canvas.draw()

def main():
    try:
        app = QApplication(sys.argv)
        loop = QEventLoop(app)
        asyncio.set_event_loop(loop)
        
        window = MainWindow()
        window.show()
        
        with loop:
            loop.run_forever()
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
