import time
from datetime import datetime
import mss
import threading
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QMessageBox, QFrame, QProgressBar)
from PySide6.QtCore import QTimer, Signal, Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QIcon, QColor
from .styles import WINDOW_STYLE, TITLE_STYLE, SUBTITLE_STYLE, TEXT_STYLE, LIGHT_OLIVE, OLIVE, PEACH, CREAM

class TimerWindow(QWidget):
    switch_task = Signal()

    def __init__(self, project_data):
        super().__init__()
        self.project_data = project_data
        self.screenshot_timer = None
        self.timer_running = False
        self.elapsed_time = 0
        self.session_goal = 3600  # Default session goal (1 hour)
        self.init_ui()
        self.check_screenshot_permission()

    def init_ui(self):
        self.setWindowTitle('Time Tracker - Timer')
        self.setGeometry(300, 300, 550, 500)
        self.setStyleSheet(WINDOW_STYLE)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Title with shadow effect
        title = QLabel('Time Tracking')
        title.setStyleSheet(f"{TITLE_STYLE} text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Project and task info card with improved styling
        info_frame = QFrame()
        info_frame.setStyleSheet(f'''
            background-color: {LIGHT_OLIVE}; 
            border-radius: 15px; 
            padding: 18px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
        ''')
        
        info_layout = QVBoxLayout()
        
        self.project_label = QLabel(f"Project: {self.project_data['project']}")
        self.project_label.setStyleSheet(f"{SUBTITLE_STYLE} margin-bottom: 5px;")
        
        self.task_label = QLabel(f"Task: {self.project_data['task']}")
        self.task_label.setStyleSheet(f"{TEXT_STYLE} font-size: 18px;")
        
        info_layout.addWidget(self.project_label)
        info_layout.addWidget(self.task_label)
        info_frame.setLayout(info_layout)
        main_layout.addWidget(info_frame)

        # Timer display with enhanced styling
        timer_frame = QFrame()
        timer_frame.setStyleSheet(f'''
            background-color: {CREAM}; 
            border: 2px solid {LIGHT_OLIVE};
            border-radius: 15px; 
            padding: 15px;
        ''')
        timer_layout = QVBoxLayout()
        
        self.time_label = QLabel('00:00:00')
        self.time_label.setStyleSheet(f'''
            font-size: 52px; 
            font-weight: bold; 
            color: {OLIVE};
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.15);
        ''')
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_layout.addWidget(self.time_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f'''
            QProgressBar {{
                border: 1px solid {LIGHT_OLIVE};
                border-radius: 10px;
                background-color: white;
                height: 15px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {PEACH};
                border-radius: 8px;
            }}
        ''')
        self.progress_bar.setRange(0, self.session_goal)
        self.progress_bar.setValue(0)
        timer_layout.addWidget(self.progress_bar)
        
        timer_frame.setLayout(timer_layout)
        main_layout.addWidget(timer_frame)

        # Control buttons with improved styling
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        # Start/Pause Button with icon styling
        self.start_pause_button = QPushButton('Start')
        self.start_pause_button.setStyleSheet(f'''
            QPushButton {{
                background-color: {PEACH};
                color: {OLIVE};
                border: none;
                border-radius: 10px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {LIGHT_OLIVE};
                transform: scale(1.05);
            }}
            QPushButton:pressed {{
                background-color: {OLIVE};
                color: {CREAM};
            }}
        ''')
        self.start_pause_button.setFixedHeight(50)
        self.start_pause_button.clicked.connect(self.toggle_timer)

        # Switch Task Button
        self.switch_task_button = QPushButton('Switch Task')
        self.switch_task_button.setStyleSheet(f'''
            QPushButton {{
                background-color: {CREAM};
                color: {OLIVE};
                border: 2px solid {LIGHT_OLIVE};
                border-radius: 10px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {LIGHT_OLIVE};
                color: {CREAM};
            }}
            QPushButton:disabled {{
                background-color: #E0E0E0;
                color: #A0A0A0;
                border: 2px solid #C0C0C0;
            }}
        ''')
        self.switch_task_button.setFixedHeight(50)
        self.switch_task_button.clicked.connect(self.handle_switch_task)
        self.switch_task_button.setEnabled(True)  # Initially enabled but will disable during tracking
        
        button_layout.addWidget(self.start_pause_button)
        button_layout.addWidget(self.switch_task_button)
        main_layout.addLayout(button_layout)
        
        # Status indicator
        self.status_label = QLabel("Ready to start tracking")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(f"color: {OLIVE}; font-size: 14px; margin-top: 10px;")
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)

        # Setup timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.setInterval(1000)  # Update every second

    def check_screenshot_permission(self):
        try:
            with mss.mss() as sct:
                sct.shot()  # Take a test screenshot
            # TODO: Send permission status to API
            return True
        except Exception as e:
            QMessageBox.warning(self, 'Warning', 
                              'Screenshot permission not granted. Please enable screen capture.')
            # TODO: Send permission status to API
            return False

    def take_screenshot(self):
        if self.timer_running:
            try:
                with mss.mss() as sct:
                    screenshot = sct.shot()
                    # TODO: Send screenshot to API
                    self.status_label.setText(f"Screenshot taken at {datetime.now().strftime('%H:%M:%S')}")
                    print(f"Screenshot taken at {datetime.now()}")
            except Exception as e:
                self.status_label.setText(f"Failed to take screenshot")
                print(f"Failed to take screenshot: {e}")

    def start_screenshot_timer(self):
        def screenshot_loop():
            while self.timer_running:
                self.take_screenshot()
                time.sleep(600)  # 10 minutes

        self.screenshot_thread = threading.Thread(target=screenshot_loop)
        self.screenshot_thread.daemon = True
        self.screenshot_thread.start()

    def toggle_timer(self):
        if not self.timer_running:
            # Starting timer
            self.timer_running = True
            self.timer.start()
            self.start_screenshot_timer()
            self.start_pause_button.setText('Pause')
            self.start_pause_button.setStyleSheet(f'''
                QPushButton {{
                    background-color: {OLIVE};
                    color: {CREAM};
                    border: none;
                    border-radius: 10px;
                    padding: 12px 24px;
                    font-weight: bold;
                    font-size: 16px;
                }}
                QPushButton:hover {{
                    background-color: #556040;
                }}
            ''')
            self.switch_task_button.setEnabled(False)  # Disable switch task during tracking
            self.status_label.setText("Tracking time...")
            # TODO: Send timer start to API
        else:
            # Pausing timer
            self.timer_running = False
            self.timer.stop()
            self.start_pause_button.setText('Resume')
            self.start_pause_button.setStyleSheet(f'''
                QPushButton {{
                    background-color: {PEACH};
                    color: {OLIVE};
                    border: none;
                    border-radius: 10px;
                    padding: 12px 24px;
                    font-weight: bold;
                    font-size: 16px;
                }}
                QPushButton:hover {{
                    background-color: {LIGHT_OLIVE};
                }}
            ''')
            self.switch_task_button.setEnabled(True)  # Enable switch task when paused
            self.status_label.setText("Tracking paused")
            # TODO: Send timer pause to API

    def update_timer(self):
        self.elapsed_time += 1
        hours = self.elapsed_time // 3600
        minutes = (self.elapsed_time % 3600) // 60
        seconds = self.elapsed_time % 60
        
        # Update timer display
        self.time_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        
        # Update progress bar (capped at 100%)
        progress = min(self.elapsed_time, self.session_goal)
        self.progress_bar.setValue(progress)
        
        # Change progress bar color as time progresses
        if self.elapsed_time >= self.session_goal:
            self.status_label.setText("Session goal achieved!")
            # Only notify once when reaching the goal
            if self.elapsed_time == self.session_goal:
                QMessageBox.information(self, "Session Goal", "You've reached your session goal!")

    def handle_switch_task(self):
        if self.timer_running:
            reply = QMessageBox.question(
                self, 'Switch Task',
                'Timer is still running. Do you want to stop and switch tasks?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.timer_running = False
                self.timer.stop()
                self.switch_task.emit()
        else:
            # Timer is already paused, just switch
            self.switch_task.emit()

    def closeEvent(self, event):
        if self.timer_running:
            reply = QMessageBox.question(
                self, 'Warning',
                'Timer is still running. Do you want to stop and exit?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.timer_running = False
                event.accept()
            else:
                event.ignore()
