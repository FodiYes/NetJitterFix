import sys
import os
import time
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QProgressBar, QCheckBox, 
                           QTabWidget, QGroupBox, QGridLayout, QMessageBox,
                           QSpacerItem, QSizePolicy, QApplication)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QFont

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import numpy as np

from utils.jitter_checker import JitterChecker
from utils.jitter_fixer import JitterFixer
from gui.theme import NeonTheme


class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        plt.style.use('dark_background')
        
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.patch.set_facecolor(NeonTheme.DARK_BG)
        
        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor(NeonTheme.DARKER_BG)
        self.axes.tick_params(colors=NeonTheme.TEXT_COLOR)
        self.axes.spines['bottom'].set_color(NeonTheme.NEON_BLUE)
        self.axes.spines['top'].set_color(NeonTheme.NEON_BLUE)
        self.axes.spines['left'].set_color(NeonTheme.NEON_BLUE)
        self.axes.spines['right'].set_color(NeonTheme.NEON_BLUE)
        
        super(MatplotlibCanvas, self).__init__(self.fig)


class JitterCheckThread(QThread):
    finished = pyqtSignal(float, list, list)
    progress_updated = pyqtSignal(int)
    
    def __init__(self, jitter_checker):
        super().__init__()
        self.jitter_checker = jitter_checker
        self.is_canceled = False
    
    def run(self):
        jitter, ping_times, time_stamps = self.jitter_checker.check_jitter(
            progress_callback=self.update_progress
        )
        self.finished.emit(jitter, ping_times, time_stamps)
    
    def update_progress(self, value):
        self.progress_updated.emit(value)
    
    def cancel(self):
        self.is_canceled = True
        self.jitter_checker.cancel_check()


class FixThread(QThread):
    progress_updated = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    
    def __init__(self, jitter_fixer, selected_fixes):
        super().__init__()
        self.jitter_fixer = jitter_fixer
        self.selected_fixes = selected_fixes
    
    def run(self):
        fix_results = {}
        total = len(self.selected_fixes)
        
        for i, fix_id in enumerate(self.selected_fixes):
            fix_name = self.jitter_fixer.fixes_available[fix_id]
            self.progress_updated.emit(int((i / total) * 100), f"Applying: {fix_name}")
            fix_results[fix_id] = self.jitter_fixer.apply_fix(fix_id)
            time.sleep(0.5)
        
        self.progress_updated.emit(100, "Fixes completed!")
        self.finished.emit(fix_results)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.jitter_checker = JitterChecker()
        self.jitter_fixer = JitterFixer()
        
        self.before_jitter = None
        self.after_jitter = None
        self.before_data = None
        self.after_data = None
        
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("NetJitterFixer")
        self.setMinimumSize(900, 700)
        
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        header_layout = QHBoxLayout()
        title_label = QLabel("NetJitterFixer")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        
        main_layout.addLayout(header_layout)
        
        tab_widget = QTabWidget()
        
        main_tab = QWidget()
        main_tab_layout = QVBoxLayout(main_tab)
        
        jitter_group = QGroupBox("Check Network Jitter")
        jitter_layout = QVBoxLayout(jitter_group)
        
        check_button_layout = QHBoxLayout()
        self.check_button = QPushButton("Check Current Jitter")
        self.check_button.clicked.connect(self.on_check_jitter)
        check_button_layout.addWidget(self.check_button)
        
        jitter_layout.addLayout(check_button_layout)
        
        self.jitter_progress = QProgressBar()
        self.jitter_progress.setVisible(False)
        jitter_layout.addWidget(self.jitter_progress)
        
        self.result_label = QLabel("Run a check to measure network jitter")
        self.result_label.setObjectName("resultLabel")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        jitter_layout.addWidget(self.result_label)
        
        main_tab_layout.addWidget(jitter_group)
        
        graph_group = QGroupBox("Charts")
        graph_layout = QVBoxLayout(graph_group)
        
        self.plot_canvas = MatplotlibCanvas(width=8, height=4, dpi=100)
        graph_layout.addWidget(self.plot_canvas)
        
        main_tab_layout.addWidget(graph_group)
        
        fix_group = QGroupBox("Fix Network Jitter")
        fix_layout = QGridLayout(fix_group)
        
        self.fix_checkboxes = {}
        all_fixes = self.jitter_fixer.get_available_fixes()
        
        row, col = 0, 0
        for fix_id, fix_name in all_fixes.items():
            checkbox = QCheckBox(fix_name)
            checkbox.setChecked(True)
            self.fix_checkboxes[fix_id] = checkbox
            fix_layout.addWidget(checkbox, row, col)
            
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        fix_button_layout = QHBoxLayout()
        self.fix_button = QPushButton("Apply Selected Fixes")
        self.fix_button.setObjectName("fixButton")
        self.fix_button.clicked.connect(self.on_fix_jitter)
        fix_button_layout.addWidget(self.fix_button)
        
        fix_layout.addLayout(fix_button_layout, row + 1, 0, 1, 2)
        
        self.fix_progress = QProgressBar()
        self.fix_progress.setVisible(False)
        fix_layout.addWidget(self.fix_progress, row + 2, 0, 1, 2)
        
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fix_layout.addWidget(self.status_label, row + 3, 0, 1, 2)
        
        main_tab_layout.addWidget(fix_group)
        
        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)
        
        about_text = QLabel(
            """<html>
            <head/><body>
            <p align="center"><span style="font-size:16pt; font-weight:600; color:#00FFFF;">NetJitterFixer</span></p>
            <p align="center"><span style="color:#FFFFFF;">A tool for fixing network jitter in Windows 10/11</span></p>
            <p align="center">&nbsp;</p>
            <p align="center"><span style="color:#39FF14;">What is jitter?</span></p>
            <p align="justify"><span style="color:#FFFFFF;">Jitter is the variation in latency of packet transmission across a network. High jitter leads to unstable network applications, particularly noticeable in online games, video conferencing, and streaming media.</span></p>
            <p align="center">&nbsp;</p>
            <p align="center"><span style="color:#39FF14;">How to use this application:</span></p>
            <p align="justify"><span style="color:#FFFFFF;">1. Measure your current jitter by clicking "Check Current Jitter"</span></p>
            <p align="justify"><span style="color:#FFFFFF;">2. Select the fixes you want to apply in the "Main" tab</span></p>
            <p align="justify"><span style="color:#FFFFFF;">3. Click "Apply Selected Fixes"</span></p>
            <p align="justify"><span style="color:#FFFFFF;">4. Check your jitter again to compare results</span></p>
            <p align="center">&nbsp;</p>
            <p align="center"><span style="color:#39FF14;">Important:</span></p>
            <p align="justify"><span style="color:#FFFFFF;">Administrator rights are required for some fixes. Make sure you run the program with administrator privileges.</span></p>
            </body></html>"""
        )
        about_text.setWordWrap(True)
        about_layout.addWidget(about_text)
        
        tab_widget.addTab(main_tab, "Main")
        tab_widget.addTab(about_tab, "About")
        
        main_layout.addWidget(tab_widget)
        
        self.setCentralWidget(central_widget)
        
        if not self.jitter_fixer.check_admin_rights():
            QMessageBox.warning(
                self,
                "Insufficient Permissions",
                "The application is running without administrator rights. Some features may not be available.\n\n"
                "It is recommended to close the application and run it as administrator."
            )
    
    def on_check_jitter(self):
        self.check_button.setEnabled(False)
        self.jitter_progress.setVisible(True)
        self.jitter_progress.setValue(0)
        self.result_label.setText("Measuring jitter...")
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.cancel_jitter_check)
        layout = self.jitter_progress.parent().layout()
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if isinstance(item, QHBoxLayout) and hasattr(item, "cancel_button_layout"):
                for j in range(item.count()):
                    widget = item.itemAt(j).widget()
                    if widget:
                        widget.deleteLater()
                layout.removeItem(item)
        
        cancel_layout = QHBoxLayout()
        cancel_layout.cancel_button_layout = True
        cancel_layout.addStretch()
        cancel_layout.addWidget(cancel_button)
        layout.insertLayout(layout.count()-1, cancel_layout)
        
        self.jitter_thread = JitterCheckThread(self.jitter_checker)
        self.jitter_thread.progress_updated.connect(self.update_check_progress)
        self.jitter_thread.finished.connect(self.on_jitter_check_complete)
        self.jitter_thread.start()

    def cancel_jitter_check(self):
        if hasattr(self, "jitter_thread") and self.jitter_thread.isRunning():
            self.jitter_thread.cancel()
            self.check_button.setEnabled(True)
            self.jitter_progress.setVisible(False)
            self.result_label.setText("Check canceled")
            
            layout = self.jitter_progress.parent().layout()
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if isinstance(item, QHBoxLayout) and hasattr(item, "cancel_button_layout"):
                    for j in range(item.count()):
                        widget = item.itemAt(j).widget()
                        if widget:
                            widget.deleteLater()
                    layout.removeItem(item)

    def update_check_progress(self, value):
        self.jitter_progress.setValue(value)
    
    def on_jitter_check_complete(self, jitter, ping_times, time_stamps):
        if self.before_jitter is None:
            self.before_jitter = jitter
            self.before_data = (ping_times, time_stamps)
            self.result_label.setText(f"Current jitter: {jitter:.2f} ms")
        else:
            self.after_jitter = jitter
            self.after_data = (ping_times, time_stamps)
            self.result_label.setText(
                f"Before fixes: {self.before_jitter:.2f} ms | "
                f"After fixes: {self.after_jitter:.2f} ms | "
                f"Improvement: {max(0, self.before_jitter - self.after_jitter):.2f} ms "
                f"({max(0, 100 - (self.after_jitter / self.before_jitter * 100)):.1f}%)"
            )
        
        self.update_plot()
        self.check_button.setEnabled(True)
        self.jitter_progress.setVisible(False)
        
        layout = self.jitter_progress.parent().layout()
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if isinstance(item, QHBoxLayout) and hasattr(item, "cancel_button_layout"):
                for j in range(item.count()):
                    widget = item.itemAt(j).widget()
                    if widget:
                        widget.deleteLater()
                layout.removeItem(item)
    
    def update_plot(self):
        self.plot_canvas.axes.clear()
        
        has_data = False
        
        if self.before_data:
            ping_times, time_stamps = self.before_data
            if ping_times and len(ping_times) > 1:
                has_data = True
                self.plot_canvas.axes.plot(
                    list(range(len(ping_times))), 
                    ping_times,
                    '-o',
                    color=NeonTheme.NEON_BLUE,
                    alpha=0.7,
                    markersize=3,
                    label="Before Fixes"
                )
                
                mean_before = np.mean(ping_times)
                self.plot_canvas.axes.axhline(
                    y=mean_before,
                    color=NeonTheme.NEON_BLUE,
                    linestyle='--',
                    alpha=0.7,
                    label=f"Average before: {mean_before:.2f} ms"
                )
        
        if self.after_data:
            ping_times, time_stamps = self.after_data
            if ping_times and len(ping_times) > 1:
                has_data = True
                self.plot_canvas.axes.plot(
                    list(range(len(ping_times))),
                    ping_times,
                    '-o',
                    color=NeonTheme.NEON_GREEN,
                    alpha=0.7,
                    markersize=3,
                    label="After Fixes"
                )
                
                mean_after = np.mean(ping_times)
                self.plot_canvas.axes.axhline(
                    y=mean_after,
                    color=NeonTheme.NEON_GREEN,
                    linestyle='--',
                    alpha=0.7,
                    label=f"Average after: {mean_after:.2f} ms"
                )
        
        self.plot_canvas.axes.set_xlabel('Ping Number', color=NeonTheme.TEXT_COLOR)
        self.plot_canvas.axes.set_ylabel('Latency (ms)', color=NeonTheme.TEXT_COLOR)
        self.plot_canvas.axes.set_title('Network Latency Chart', color=NeonTheme.NEON_BLUE)
        self.plot_canvas.axes.grid(True, linestyle='--', alpha=0.3)
        
        if has_data:
            self.plot_canvas.axes.legend()
        
        self.plot_canvas.fig.subplots_adjust(left=0.12, bottom=0.12, right=0.95, top=0.92)
        
        self.plot_canvas.draw()
    
    def on_fix_jitter(self):
        selected_fixes = [fix_id for fix_id, checkbox in self.fix_checkboxes.items() if checkbox.isChecked()]
        
        if not selected_fixes:
            QMessageBox.warning(self, "Warning", "No fixes selected!")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm",
            "Are you sure you want to apply the selected fixes?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        self.fix_button.setEnabled(False)
        self.fix_progress.setVisible(True)
        self.fix_progress.setValue(0)
        self.status_label.setText("Applying fixes...")
        
        self.fix_thread = FixThread(self.jitter_fixer, selected_fixes)
        self.fix_thread.progress_updated.connect(self.update_fix_progress)
        self.fix_thread.finished.connect(self.on_fix_complete)
        self.fix_thread.start()
    
    def update_fix_progress(self, value, status):
        self.fix_progress.setValue(value)
        self.status_label.setText(status)
    
    def on_fix_complete(self, results):
        success_count = sum(1 for success in results.values() if success)
        
        self.status_label.setText(
            f"Fixes successfully applied: {success_count}/{len(results)}"
        )
        
        QMessageBox.information(
            self,
            "Fixes Applied",
            f"Fixes applied: {success_count} of {len(results)}.\n\n"
            "It is recommended to check your jitter again to compare results."
        )
        
        self.fix_button.setEnabled(True)
