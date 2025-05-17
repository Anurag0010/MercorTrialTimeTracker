import time
import os
from datetime import datetime, timedelta
import mss
import threading
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QMessageBox, QFrame, QProgressBar)
from PySide6.QtCore import QTimer, Signal, Qt, QPropertyAnimation, QEasingCurve, QSize, QRect, Property
from PySide6.QtGui import QFont, QIcon, QColor, QPixmap, QKeySequence, QShortcut
from .styles import (WINDOW_STYLE, TITLE_STYLE, SUBTITLE_STYLE, TEXT_STYLE, 
                    PRIMARY, SECONDARY, TERTIARY, DARK_PRIMARY, LIGHT_PRIMARY,
                    SUCCESS, WARNING, DANGER, INFO, WHITE, GRAY, DARK_GRAY, BLACK, 
                    CARD_STYLE, SHADOW, GRADIENT_BUTTON)
from .api_service import APIService
from .constants import TIMELOG_INTERVAL_SECONDS, PROGRESS_BAR_FOR_SESSION

class PulsingLabel(QLabel):
    """A custom label that can pulse when timer is active"""
    
    def __init__(self, text='', parent=None):
        super().__init__(text, parent)
        self._opacity = 1.0
        self._pulsing = False
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._update_pulse)
        self._pulse_timer.setInterval(40)  # 25fps animation
        self._pulse_direction = 1  # 1 for fading out, -1 for fading in
        
    def _update_pulse(self):
        if self._pulsing:
            min_opacity = 0.7
            max_opacity = 1.0
            step = 0.02
            
            self._opacity += step * self._pulse_direction
            
            if self._opacity >= max_opacity:
                self._opacity = max_opacity
                self._pulse_direction = 1  # Start fading out
            elif self._opacity <= min_opacity:
                self._opacity = min_opacity
                self._pulse_direction = -1  # Start fading in
                
            # Update opacity
            self.setStyleSheet(f"""
                font-size: 72px;
                font-weight: 700;
                color: {PRIMARY};
                letter-spacing: 4px;
                text-shadow: 0 2px 8px rgba(99, 102, 241, 0.2);
                opacity: {self._opacity};
            """)
    
    def start_pulsing(self):
        self._pulsing = True
        self._pulse_timer.start()
        
    def stop_pulsing(self):
        self._pulsing = False
        self._pulse_timer.stop()
        self._opacity = 1.0
        self.setStyleSheet(f"""
            font-size: 72px;
            font-weight: 700;
            color: {PRIMARY};
            letter-spacing: 4px;
            text-shadow: 0 2px 8px rgba(99, 102, 241, 0.2);
        """)

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
        self.session_goal = PROGRESS_BAR_FOR_SESSION  # Using the constant from constants.py
        self.start_time = None
        self.last_timelog_time = None
        self.screenshot_interval = TIMELOG_INTERVAL_SECONDS  # Using the constant from constants.py
        self.screenshots_folder = "screenshots"
        self.init_ui()
        self.setup_connections()
        self.ensure_screenshots_folder_exists()
        self.setup_shortcuts()
        
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
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {SECONDARY}, stop:1 {PRIMARY});
                    color: {WHITE};
                    border: none;
                    border-radius: 12px;
                    padding: 12px 24px;
                    font-weight: bold;
                    font-size: 16px;
                    box-shadow: {SHADOW};
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {PRIMARY}, stop:1 {SECONDARY});
                    transform: translateY(-2px);
                }}
                QPushButton:pressed {{
                    background: {DARK_PRIMARY};
                    transform: translateY(1px);
                }}
            ''')
            
            # Start pulsing effect for timer
            self.time_label.start_pulsing()
            
            # Animate progress bar
            self._animate_progress_bar()
            
            # Disable the switch task button during active tracking
            self.switch_task_button.setEnabled(False)
            self.status_label.setText("Tracking active")
            self.status_icon.setPixmap(self._create_status_icon(SUCCESS))
            
            # Take initial screenshot and post first timelog
            self.take_screenshot_and_post_timelog()
            
            # Start periodic screenshot/timelog
            self.start_periodic_tasks()
            
            # Verify screenshot permission
            # self.check_screenshot_permission()

    def init_ui(self):
        self.setWindowTitle('Time Tracker – Timer')
        self.setGeometry(300, 300, 600, 650)
        self.setStyleSheet(WINDOW_STYLE + f"""
            QWidget {{
                background-image: url('data:image/png;base64,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');
                background-position: center;
                background-size: auto;
                background-color: {WHITE};
            }}
        """)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(40, 40, 40, 40)

        # Header with enhanced gradient background
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {PRIMARY}, stop:0.5 {SECONDARY}, stop:1 {TERTIARY});
                border-radius: 16px;
                min-height: 75px;
                box-shadow: {SHADOW};
            }}
        """)
        header_layout = QHBoxLayout(header_frame)
        
        title = QLabel('Time Tracking')
        title.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 700;
            color: {WHITE};
            letter-spacing: 0.5px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.logout_button = QPushButton("Logout")
        self.logout_button.setFixedWidth(100)
        self.logout_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logout_button.setStyleSheet(f'''
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.15);
                color: {WHITE};
                border: 1px solid {WHITE};
                border-radius: 10px;
                padding: 8px 15px;
                font-size: 14px;
                font-weight: 600;
                transition: all 0.2s;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.25);
            }}
            QPushButton:pressed {{
                background-color: rgba(255, 255, 255, 0.1);
            }}
        ''')
        self.logout_button.clicked.connect(self.handle_logout)  # Connect logout button to handler
        
        header_layout.addWidget(self.logout_button)
        header_layout.addWidget(title)
        header_layout.addSpacing(100)  # Balance out the logout button
        
        main_layout.addWidget(header_frame)
        
        # Project and Task Information Card
        info_frame = QFrame()
        info_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {WHITE};
                border: 1px solid {LIGHT_PRIMARY};
                border-radius: 12px;
                padding: 20px;
                box-shadow: {SHADOW};
            }}
        """)
        info_layout = QVBoxLayout(info_frame)
        
        # Project info
        project_label = QLabel(f"Project: {self.project_data.get('project_name', 'Unknown Project')}")
        project_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 600;
            color: {PRIMARY};
            margin-bottom: 5px;
        """)
        
        # Task info
        task_label = QLabel(f"Task: {self.project_data.get('task_name', 'Unknown Task')}")
        task_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 500;
            color: {SECONDARY};
            margin-bottom: 5px;
        """)
        
        info_layout.addWidget(project_label)
        info_layout.addWidget(task_label)
        
        main_layout.addWidget(info_frame)
        
        # Timer Display
        timer_frame = QFrame()
        timer_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                         stop:0 {WHITE}, 
                                         stop:1 {LIGHT_PRIMARY});
                border-radius: 16px;
                padding: 20px;
                box-shadow: {SHADOW};
            }}
        """)
        timer_layout = QVBoxLayout(timer_frame)
        
        self.time_label = PulsingLabel("00:00:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Timer progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 5px;
                background-color: rgba(203, 213, 225, 0.3);
                max-height: 8px;
            }}
            
            QProgressBar::chunk {{
                border-radius: 5px;
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {PRIMARY}, stop:0.5 {SECONDARY}, stop:1 {TERTIARY});
            }}
        """)
        
        # Status indicator
        status_row = QHBoxLayout()
        self.status_icon = QLabel()
        self.status_icon.setFixedSize(16, 16)
        self.status_icon.setPixmap(self._create_status_icon(DARK_GRAY))
        
        self.status_label = QLabel("Ready to start")
        self.status_label.setStyleSheet(f"""
            color: {DARK_GRAY};
            font-size: 14px;
        """)
        
        status_row.addWidget(self.status_icon)
        status_row.addWidget(self.status_label)
        status_row.addStretch()
        
        timer_layout.addWidget(self.time_label)
        timer_layout.addWidget(self.progress_bar)
        timer_layout.addLayout(status_row)
        
        main_layout.addWidget(timer_frame)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_pause_button = QPushButton("Start")
        self.start_pause_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_pause_button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {SECONDARY}, stop:1 {PRIMARY});
                color: {WHITE};
                border: none;
                border-radius: 12px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: bold;
                box-shadow: {SHADOW};
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {TERTIARY}, stop:1 {SECONDARY});
            }}
            QPushButton:pressed {{
                background: {DARK_PRIMARY};
            }}
        """)
        self.start_pause_button.clicked.connect(self.toggle_timer)  # Connect the button to toggle_timer
        
        self.switch_task_button = QPushButton("Switch Task")
        self.switch_task_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.switch_task_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {WHITE};
                color: {PRIMARY};
                border: 2px solid {PRIMARY};
                border-radius: 12px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {LIGHT_PRIMARY};
            }}
            QPushButton:pressed {{
                background-color: {LIGHT_PRIMARY};
                border-color: {DARK_PRIMARY};
                color: {DARK_PRIMARY};
            }}
            QPushButton:disabled {{
                background-color: {WHITE};
                color: {DARK_GRAY};
                border-color: {DARK_GRAY};
            }}
        """)
        self.switch_task_button.clicked.connect(self.handle_switch_task)  # Connect switch task button to handler
        
        button_layout.addWidget(self.switch_task_button)
        button_layout.addWidget(self.start_pause_button)
        
        main_layout.addLayout(button_layout)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        
        # Setup timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.setInterval(1000)  # Update every second
        
    def setup_shortcuts(self):
        """Setup keyboard shortcuts for common actions"""
        # Shortcut for Start/Pause - Space bar
        start_pause_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        start_pause_shortcut.activated.connect(self.toggle_timer)
        
        # Shortcut for Switch Task - Ctrl+T
        switch_task_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        switch_task_shortcut.activated.connect(self.handle_switch_task)
        
        # Shortcut for Logout - Ctrl+L
        logout_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        logout_shortcut.activated.connect(self.handle_logout)
        
    def _animate_progress_bar(self):
        """Animate progress bar when value changes"""
        if hasattr(self, 'progress_animation'):
            self.progress_animation.stop()
            
        # Calculate the percentage of elapsed time relative to session goal
        progress_percentage = min(int((self.elapsed_time / self.session_goal) * 100), 100)
            
        self.progress_animation = QPropertyAnimation(self.progress_bar, b"value")
        self.progress_animation.setDuration(300)
        self.progress_animation.setStartValue(self.progress_bar.value())
        self.progress_animation.setEndValue(progress_percentage)
        self.progress_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.progress_animation.start()
        
    def _create_colored_circle(self, color, radius):
        """Create a colored circle icon"""
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        from PySide6.QtGui import QPainter, QPen, QBrush
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(color)))
        painter.setPen(QPen(QColor(color), 0))
        painter.drawEllipse(12 - radius, 12 - radius, radius * 2, radius * 2)
        painter.end()
        
        return pixmap
    
    def _create_status_icon(self, color):
        """Create a status icon (colored dot)"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        from PySide6.QtGui import QPainter, QPen, QBrush
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(color)))
        painter.setPen(QPen(QColor(color), 0))
        painter.drawEllipse(3, 3, 10, 10)
        painter.end()
        
        return pixmap
        
    def setup_connections(self):
        """Set up signal/slot connections for API service"""
        self.api_service.screenshot_posted.connect(self.on_screenshot_success)
        self.api_service.screenshot_error.connect(self.on_api_error)
        self.api_service.timelog_posted.connect(self.on_timelog_success)
        self.api_service.timelog_error.connect(self.on_api_error)
        self.api_service.token_expired.connect(self.handle_token_expired)

    def handle_token_expired(self):
        """Handle logout request."""
        # Ensure timer is stopped
        if self.timer_running:
            self.toggle_timer() 
        """Handle token expiration by logging out the user"""
        #self.logout_requested.emit()
    
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
                
                # Update status with animation
                self.status_label.setText(f"Screenshot taken at {current_time.strftime('%H:%M:%S')}")
                
                # Flash effect to indicate screenshot was taken
                self._flash_status()
                
            except Exception as e:
                self.status_label.setText(f"Failed to take screenshot: {str(e)}")
                print(f"Failed to take screenshot: {e}")
    
    def _flash_status(self):
        """Create a flash animation for the status label"""
        original_style = self.status_label.styleSheet()
        
        # Flash effect using animation
        flash_animation = QPropertyAnimation(self, b"status_opacity")
        flash_animation.setDuration(500)
        flash_animation.setStartValue(1.0)
        flash_animation.setKeyValueAt(0.5, 0.3)
        flash_animation.setEndValue(1.0)
        flash_animation.setEasingCurve(QEasingCurve.Type.OutInQuad)
        
        # We need to set a property for the animation to work
        def set_status_opacity(opacity):
            self.status_label.setStyleSheet(f"""
                color: {MEDIUM_BLUE};
                font-size: 14px;
                font-weight: bold;
                opacity: {opacity};
            """)
            
        self._status_opacity = 1.0
        
        # Create a property to animate
        def get_status_opacity():
            return self._status_opacity
            
        def set_status_opacity(opacity):
            self._status_opacity = opacity
            self.status_label.setStyleSheet(f"""
                color: {MEDIUM_BLUE};
                font-size: 14px;
                font-weight: bold;
                opacity: {opacity};
            """)
            
        # Create the property to animate
        status_opacity = Property(float, get_status_opacity, set_status_opacity)
        
        flash_animation.start()
        
        # Restore original style after animation
        QTimer.singleShot(1000, lambda: self.status_label.setStyleSheet(original_style))

    def start_periodic_tasks(self):
        """Start periodic screenshot and timelog tasks"""
        # Create and start a timer for screenshots
        self.screenshot_timer = QTimer()
        self.screenshot_timer.timeout.connect(self.take_screenshot_and_post_timelog)
        self.screenshot_timer.setInterval(self.screenshot_interval * 1000)  # Convert seconds to milliseconds
        self.screenshot_timer.start()

        # Initialize last timelog time
        self.last_timelog_time = datetime.now()

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
            
            # Stop the pulsing effect
            self.time_label.stop_pulsing()
            
            # Stop periodic tasks
            self.stop_periodic_tasks()
            
            # Calculate end time
            end_time = datetime.now()
            
            # Update UI
            self.start_pause_button.setText('Resume')
            self.start_pause_button.setStyleSheet(f'''
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {LIGHT_PRIMARY}, stop:1 {SECONDARY});
                    color: {PRIMARY};
                    border: none;
                    border-radius: 12px;
                    padding: 12px 24px;
                    font-weight: bold;
                    font-size: 16px;
                    box-shadow: {SHADOW};
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {SECONDARY}, stop:1 {PRIMARY});
                    transform: translateY(-2px);
                }}
                QPushButton:pressed {{
                    background: {DARK_PRIMARY};
                    transform: translateY(1px);
                }}
            ''')
            self.switch_task_button.setEnabled(True)  # Enable switch task when paused
            
            # Update status icon and text
            self.status_icon.setPixmap(self._create_status_icon("#F59E0B"))  # Yellow for paused
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
        """Update the timer display."""
        self.elapsed_time += 1
        hours, remainder = divmod(self.elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
        self.time_label.setText(time_str)
        
        # Update progress bar with animation
        if self.elapsed_time <= self.session_goal:
            self._animate_progress_bar()
        
    def handle_switch_task(self):
        """Handle switching to a different task."""
        # Ensure timer is stopped
        if self.timer_running:
            self.toggle_timer()  # This will stop the timer and post final timelog
        
        # Emit signal to navigate back to project/task selection
        self.switch_task.emit()
    
    def handle_logout(self):
        """Handle logout request."""
        # Ensure timer is stopped
        if self.timer_running:
            self.toggle_timer()  # This will stop the timer and post final timelog
            
        # Ask for confirmation - using a better approach for creating the message box
        msg_box = QMessageBox()
        msg_box.setWindowTitle('Confirm Logout')
        msg_box.setText('Are you sure you want to log out? Any unsaved progress will be lost.')
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        msg_box.setIcon(QMessageBox.Icon.Question)
        
        # Execute the dialog and check the result
        result = msg_box.exec()
        
        if result == QMessageBox.StandardButton.Yes:
            # Emit signal to navigate back to auth screen
            self.logout_requested.emit()
    
    def on_screenshot_success(self):
        """Handle successful screenshot post."""
        current_time = datetime.now().strftime('%H:%M:%S')
        self.status_label.setText(f"Screenshot uploaded at {current_time}")
        
        # Clean up screenshots that are older than 5 minutes
        self.clean_up_screenshots()
    
    def clean_up_screenshots(self):
        """Delete old screenshot files to save storage space"""
        try:
            # Keep only the most recent screenshots and delete older ones
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(minutes=5)  # Keep screenshots from last 5 minutes
            
            count = 0
            for filename in os.listdir(self.screenshots_folder):
                if filename.startswith('screenshot_') and filename.endswith('.png'):
                    file_path = os.path.join(self.screenshots_folder, filename)
                    
                    # Extract the timestamp from the filename
                    try:
                        # Format: screenshot_YYYYMMDD_HHMMSS.png
                        date_part = filename.split('_')[1]
                        time_part = filename.split('_')[2].split('.')[0]
                        timestamp_str = f"{date_part}_{time_part}"
                        file_time = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                        
                        # Delete files older than the cutoff time
                        if file_time < cutoff_time:
                            os.remove(file_path)
                            count += 1
                    except (IndexError, ValueError):
                        # Skip files that don't match the expected format
                        pass
            
            if count > 0:
                print(f"Cleaned up {count} old screenshot files")
        except Exception as e:
            print(f"Error cleaning up screenshots: {e}")
    
    def on_timelog_success(self):
        """Handle successful timelog post."""
        current_time = datetime.now().strftime('%H:%M:%S')
        self.status_label.setText(f"Time logged at {current_time}")
    
    def on_api_error(self, error_message):
        """Handle API error."""
        self.status_label.setText(f"Error: {error_message}")
        
    def closeEvent(self, event):
        """Handle window close event."""
        # Ensure timer is stopped
        if self.timer_running:
            self.toggle_timer()  # This will stop the timer and post final timelog
            
        # Ask for confirmation
        confirm = QMessageBox.question(
            self, 
            'Confirm Exit', 
            'Are you sure you want to exit? Any unsaved progress will be lost.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
