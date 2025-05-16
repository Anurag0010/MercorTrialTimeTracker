from PySide6.QtWidgets import QMainWindow, QStackedWidget
from .styles import WINDOW_STYLE
from .auth_window import AuthWindow
from .dashboard_window import DashboardWindow
from .project_window import ProjectWindow
from .timer_window import TimerWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Time Tracker')
        self.setGeometry(200, 200, 800, 600)
        self.setStyleSheet(WINDOW_STYLE)

        # Create stacked widget to manage different windows
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create and add windows
        self.auth_window = AuthWindow()
        self.dashboard_window = DashboardWindow()
        self.project_window = ProjectWindow()
        
        self.stacked_widget.addWidget(self.auth_window)
        self.stacked_widget.addWidget(self.dashboard_window)
        self.stacked_widget.addWidget(self.project_window)

        # Connect signals
        self.auth_window.login_successful.connect(self.show_dashboard_window)
        self.dashboard_window.task_clicked.connect(self.show_timer_window)
        self.project_window.task_selected.connect(self.show_timer_window)

    def show_dashboard_window(self):
        self.stacked_widget.setCurrentWidget(self.dashboard_window)
        
    def show_project_window(self):
        self.stacked_widget.setCurrentWidget(self.project_window)

    def show_timer_window(self, project_data):
        self.timer_window = TimerWindow(project_data)
        self.stacked_widget.addWidget(self.timer_window)
        self.stacked_widget.setCurrentWidget(self.timer_window)
        self.timer_window.switch_task.connect(self.handle_switch_task)

    def handle_switch_task(self):
        self.stacked_widget.setCurrentWidget(self.dashboard_window)
