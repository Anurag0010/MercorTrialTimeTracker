import time
import os
from datetime import datetime, timedelta
import mss
import threading
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QMessageBox, QFrame, QProgressBar)
from PySide6.QtCore import QTimer, Signal, Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QIcon, QColor
from .styles import WINDOW_STYLE, TITLE_STYLE, SUBTITLE_STYLE, TEXT_STYLE, LIGHT_OLIVE, OLIVE, PEACH, CREAM
from .api_service import APIService
from .constants import TIMELOG_INTERVAL_SECONDS

class TimerWindow(QWidget):
    switch_task = Signal()
    logout_requested = Signal()

    def __init__(self, project_data, api_service=None):
        super().__init__()
        self.project_data = project_data  # Should contain both project and task
        self.api_service = api_service or APIService.get_instance()
        self.screenshot_timer = None
        self.timelog_timer = None
        self.timer_running = False
        self.elapsed_time = 0
        self.session_goal = 3600  # Default session goal (1 hour)
        self.start_time = None
        self.last_timelog_time = None
        self.screenshot_interval = 10  # Seconds between screenshots for testing (change to desired value)
        self.screenshots_folder = "screenshots"
        self.init_ui()
        self.setup_connections()
        self.ensure_screenshots_folder_exists()
        
    def start_timer(self):
        """Start the time tracking timer."""
        if not self.timer_running:
            self.timer_running = True
            self.start_time = datetime.now()
            self.last_timelog_time = self.start_time
            self.timer.start()
            
            # Update button style and text
            self.start_pause_button.setText('Pause')
            self.start_pause_button.setStyleSheet(f'''
                QPushButton {{
                    background-color: {LIGHT_OLIVE};
                    color: {OLIVE};
                    border: none;
                    border-radius: 10px;
                    padding: 12px 24px;
                    font-weight: bold;
                    font-size: 16px;
                }}
                QPushButton:hover {{
                    background-color: {PEACH};
                }}
            ''')
            
            # Disable the switch task button during active tracking
            self.switch_task_button.setEnabled(False)
            self.status_label.setText("Tracking active")
            
            # Take initial screenshot and post first timelog
            self.take_screenshot_and_post_timelog()
            
            # Start periodic screenshot/timelog
            self.start_periodic_tasks()
            
            # Verify screenshot permission
            self.check_screenshot_permission()

    def init_ui(self):
        self.setWindowTitle('Time Tracker – Timer')
        self.setGeometry(300, 300, 570, 540)
        self.setStyleSheet(WINDOW_STYLE)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(28)
        main_layout.setContentsMargins(38, 38, 38, 38)

        # Header with title and logout button
        header_layout = QHBoxLayout()
        title = QLabel('Time Tracking')
        title.setStyleSheet(TITLE_STYLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logout_button = QPushButton("Logout")
        self.logout_button.setFixedWidth(90)
        self.logout_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logout_button.setStyleSheet('font-size: 15px; font-weight: 700;')
        self.logout_button.clicked.connect(self.handle_logout)
        header_layout.addWidget(title, 1)
        header_layout.addWidget(self.logout_button, 0)
        main_layout.addLayout(header_layout)

        # Project and task info card with improved styling
        from .styles import CARD_STYLE, PRIMARY, ACCENT, SUBTITLE_STYLE, TEXT_STYLE
        info_frame = QFrame()
        info_frame.setStyleSheet(CARD_STYLE)
        info_layout = QVBoxLayout()
        self.project_label = QLabel(f"Project: {self.project_data.get('project_name', 'Unknown Project')}")
        self.project_label.setStyleSheet(f"{SUBTITLE_STYLE} margin-bottom: 5px;")
        self.task_label = QLabel(f"Task: {self.project_data.get('task_name', 'Unknown Task')}")
        self.task_label.setStyleSheet(f"{TEXT_STYLE} font-size: 18px;")
        info_layout.addWidget(self.project_label)
        info_layout.addWidget(self.task_label)
        info_frame.setLayout(info_layout)
        main_layout.addWidget(info_frame)

        # Timer display with enhanced styling
        timer_frame = QFrame()
        timer_frame.setStyleSheet(CARD_STYLE)
        timer_layout = QVBoxLayout()
        self.time_label = QLabel('00:00:00')
        self.time_label.setStyleSheet(f'font-size: 56px; font-weight: 800; color: {PRIMARY}; letter-spacing: 2px;')
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
        
    def setup_connections(self):
        """Set up signal/slot connections for API service"""
        self.api_service.screenshot_posted.connect(self.on_screenshot_success)
        self.api_service.screenshot_error.connect(self.on_api_error)
        self.api_service.timelog_posted.connect(self.on_timelog_success)
        self.api_service.timelog_error.connect(self.on_api_error)

    def ensure_screenshots_folder_exists(self):
        """Ensure the screenshots directory exists"""
        if not os.path.exists(self.screenshots_folder):
            os.makedirs(self.screenshots_folder)

    def check_screenshot_permission(self):
        try:
            with mss.mss() as sct:
                sct.shot(output=os.path.join(self.screenshots_folder, 'permission_test.png'))
            
            # Send permission status to API
            self.api_service.check_screenshot_permission()
            return True
        except Exception as e:
            QMessageBox.warning(self, 'Warning', 
                              'Screenshot permission not granted. Please enable screen capture.')
            
            # Send permission status to API (permission denied)
            # Note: In a real implementation, you would adjust this to indicate lack of permission
            self.api_service.check_screenshot_permission()
            return False

    def take_screenshot_and_post_timelog(self):
        """Take a screenshot and post the timelog with screenshot to the API"""
        if self.timer_running:
            try:
                # Get current timestamp
                current_time = datetime.now()
                
                # Generate filename for screenshot
                filename = os.path.join(
                    self.screenshots_folder,
                    f'screenshot_{current_time.strftime("%Y%m%d_%H%M%S")}.png'
                )
                
                # Take the screenshot
                with mss.mss() as sct:
                    # Capture the whole screen
                    sct.shot(output=filename)
                
                # Calculate duration since start or last timelog
                duration_seconds = (current_time - self.last_timelog_time).total_seconds()
                
                # Post timelog with screenshot to API
                start_time = self.last_timelog_time
                end_time = current_time
                
                # Update last timelog time
                self.last_timelog_time = current_time
                
                # Post to API
                self.api_service.post_timelog_with_screenshot(
                    self.project_data.get('task_id', ''),
                    self.project_data.get('project_id', ''),
                    start_time.isoformat(),
                    end_time.isoformat(),
                    int(duration_seconds)
                )
                
                self.status_label.setText(f"Screenshot taken at {current_time.strftime('%H:%M:%S')}")
                
            except Exception as e:
                self.status_label.setText(f"Failed to take screenshot: {str(e)}")
                print(f"Failed to take screenshot: {e}")

    def start_periodic_tasks(self):
        """Start periodic screenshot and timelog tasks"""
        # Create and start a timer for screenshots
        self.screenshot_timer = QTimer()
        self.screenshot_timer.timeout.connect(self.take_screenshot_and_post_timelog)
        self.screenshot_timer.setInterval(self.screenshot_interval * 1000)  # Convert seconds to milliseconds
        self.screenshot_timer.start()

    def stop_periodic_tasks(self):
        """Stop periodic screenshot and timelog tasks"""
        if self.screenshot_timer:
            self.screenshot_timer.stop()

    def toggle_timer(self):
        """Toggle timer between start and pause states"""
        if not self.timer_running:
            # Start timer
            self.start_timer()
        else:
            # Pause timer
            self.timer_running = False
            self.timer.stop()
            
            # Stop periodic tasks
            self.stop_periodic_tasks()
            
            # Calculate end time
            end_time = datetime.now()
            
            # Update UI
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
            
            # Post final timelog for this session
            if self.start_time:
                duration_seconds = (end_time - self.last_timelog_time).total_seconds()
                
                # Post to API
                self.api_service.post_timelog_with_screenshot(
                    self.project_data.get('task_id', ''),
                    self.project_data.get('project_id', ''),
                    self.last_timelog_time.isoformat(),
                    end_time.isoformat(),
                    int(duration_seconds)
                )

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
                self.stop_periodic_tasks()
                end_time = datetime.now()
                
                # Log the completed time session
                if self.start_time:
                    duration_seconds = (end_time - self.last_timelog_time).total_seconds()
                    
                    # Post final timelog for this session
                    self.api_service.post_timelog_with_screenshot(
                        self.project_data.get('task_id', ''),
                        self.project_data.get('project_id', ''),
                        self.last_timelog_time.isoformat(),
                        end_time.isoformat(),
                        int(duration_seconds)
                    )
                
                self.switch_task.emit()
        else:
            # Timer is already paused, just switch
            self.switch_task.emit()
            
    def on_screenshot_success(self, success):
        """Handler for successful screenshot upload"""
        if success:
            print("Screenshot uploaded successfully")
    
    def on_timelog_success(self, success):
        """Handler for successful timelog posting"""
        if success:
            print("Time log posted successfully")
    
    def on_api_error(self, error_msg):
        """Handler for API errors"""
        print(f"API Error: {error_msg}")
        # We don't show a message box here to avoid interrupting the user's workflow,
        # but in a production app you might want to log this or show a non-intrusive notification

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
                self.timer.stop()
                self.stop_periodic_tasks()
                end_time = datetime.now()
                
                # Log the completed time session
                if self.start_time:
                    duration_seconds = (end_time - self.last_timelog_time).total_seconds()
                    
                    # Post final timelog
                    self.api_service.post_timelog_with_screenshot(
                        self.project_data.get('task_id', ''),
                        self.project_data.get('project_id', ''),
                        self.last_timelog_time.isoformat(),
                        end_time.isoformat(),
                        int(duration_seconds)
                    )
                
                event.accept()
            else:
                event.ignore()

    def handle_logout(self):
        """Handle logout button click"""
        if self.timer_running:
            reply = QMessageBox.question(
                self, 'Confirm Logout',
                'Timer is still running. Do you want to stop and log out?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
                
            # Stop timer and log final time session
            self.timer_running = False
            self.timer.stop()
            self.stop_periodic_tasks()
            end_time = datetime.now()
            
            if self.start_time:
                duration_seconds = (end_time - self.last_timelog_time).total_seconds()
                
                # Post final timelog
                self.api_service.post_timelog_with_screenshot(
                    self.project_data.get('task_id', ''),
                    self.project_data.get('project_id', ''),
                    self.last_timelog_time.isoformat(),
                    end_time.isoformat(),
                    int(duration_seconds)
                )
            
        # Perform logout
        self.api_service.logout()
        
        # Signal will be caught by main window
        self.logout_requested.emit()
