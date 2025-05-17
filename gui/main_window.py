from PySide6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox
from .styles import WINDOW_STYLE
from .auth_window import AuthWindow
from .dashboard_window import DashboardWindow
from .project_window import ProjectWindow
from .timer_window import TimerWindow
from .api_service import APIService

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Create a single instance of API service to be shared across all windows
        self.api_service = APIService.get_instance()
        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        self.setWindowTitle('Time Tracker')
        self.setGeometry(200, 200, 900, 700)
        self.setStyleSheet(WINDOW_STYLE)

        # Create stacked widget to manage different windows
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create and add windows
        self.auth_window = AuthWindow(api_service=self.api_service)
        self.auth_window.api_service = self.api_service  # Pass API service to auth window
        
        self.dashboard_window = DashboardWindow(api_service=self.api_service)
        # Pass API service if dashboard window needs it
        
        self.project_window = ProjectWindow(api_service=self.api_service)
        
        self.stacked_widget.addWidget(self.auth_window)
        self.stacked_widget.addWidget(self.dashboard_window)
        self.stacked_widget.addWidget(self.project_window)

        # Connect signals
        self.auth_window.login_successful.connect(self.show_dashboard_window)  # Changed to show dashboard after login
        self.dashboard_window.task_clicked.connect(self.show_timer_window)
        self.project_window.task_selected.connect(self.handle_task_selected)

    def setup_connections(self):
        """Set up signal connections for API service"""
        # Connect token expired signal to redirect to login
        self.api_service.token_expired.connect(self.handle_token_expired)
        self.api_service.logout_success.connect(self.show_login_window)
        # Connect projects and tasks loaded signal to update dashboard
        self.api_service.projects_and_tasks_loaded.connect(self.update_dashboard)

    def show_dashboard_window(self):
        """Show dashboard window and fetch tasks"""
        print("Showing dashboard window and fetching tasks...")
        # Fetch all projects and tasks for the employee
        self.api_service.get_projects_and_tasks()
        self.stacked_widget.setCurrentWidget(self.dashboard_window)
        
    def update_dashboard(self, projects_data):
        """Update dashboard with fetched projects and tasks"""
        print(f"Updating dashboard with {len(projects_data)} projects")
        self.dashboard_window.update_projects(projects_data)
        
    def show_project_window(self):
        # Optionally refresh projects here:
        self.stacked_widget.setCurrentWidget(self.project_window)
        self.api_service.get_projects_and_tasks()
        
    def handle_task_selected(self, selection):
        """Handle when a task is selected in ProjectWindow and start timer."""
        project = selection.get('project')
        task = selection.get('task')
        
        # Check if we already have a timer window in the stack
        timer_windows = [
            self.stacked_widget.widget(i) 
            for i in range(self.stacked_widget.count()) 
            if isinstance(self.stacked_widget.widget(i), TimerWindow)
        ]
        
        # Remove old timer windows to prevent memory leaks
        for old_timer in timer_windows:
            self.stacked_widget.removeWidget(old_timer)
            if hasattr(old_timer, 'deleteLater'):
                old_timer.deleteLater()
    
        self.timer_window = TimerWindow(project_data={'project': project, 'task': task}, api_service=self.api_service)
        # Connect the switch_task signal from timer window
        self.timer_window.switch_task.connect(self.handle_switch_task)
        self.timer_window.logout_requested.connect(self.logout_user)
        self.stacked_widget.addWidget(self.timer_window)
        self.stacked_widget.setCurrentWidget(self.timer_window)
        # Optionally, call a start method on TimerWindow if needed

    def show_timer_window(self, project_data):
        """Show timer window for the selected task"""
        print(f"Starting timer for {project_data}")
        
        # Check if we already have a timer window in the stack
        timer_windows = [
            self.stacked_widget.widget(i) 
            for i in range(self.stacked_widget.count()) 
            if isinstance(self.stacked_widget.widget(i), TimerWindow)
        ]
        
        # Remove old timer windows to prevent memory leaks
        for old_timer in timer_windows:
            self.stacked_widget.removeWidget(old_timer)
            if hasattr(old_timer, 'deleteLater'):
                old_timer.deleteLater()
    
        # Create new timer window
        self.timer_window = TimerWindow(project_data, api_service=self.api_service)
        # Connect the switch_task signal from timer window
        self.timer_window.switch_task.connect(self.handle_switch_task)
        self.timer_window.logout_requested.connect(self.logout_user)
        self.stacked_widget.addWidget(self.timer_window)
        self.stacked_widget.setCurrentWidget(self.timer_window)
        # Start the timer automatically
        self.timer_window.start_timer()

    def show_login_window(self):
        """Switch back to login window"""
        # Reset auth window if necessary
        self.auth_window = AuthWindow(api_service=self.api_service)
        self.auth_window.api_service = self.api_service
        self.auth_window.login_successful.connect(self.show_dashboard_window)  # Changed to show dashboard
        
        # Replace the old auth window with the new one
        self.stacked_widget.removeWidget(self.stacked_widget.widget(0))
        self.stacked_widget.insertWidget(0, self.auth_window)
        
        # Switch to login window
        self.stacked_widget.setCurrentWidget(self.auth_window)

    def handle_switch_task(self):
        """Handle switch task request from timer window"""
        print("Switching task - returning to dashboard")
        # Return to dashboard when switching tasks
        self.show_dashboard_window()
        
    def handle_token_expired(self):
        """Handle expired token by showing message and redirecting to login"""
        QMessageBox.warning(
            self, 
            "Session Expired", 
            "Your session has expired. Please log in again."
        )
        self.show_login_window()
        
    def logout_user(self):
        """Log out the current user"""
        # The actual logout API call is handled in timer_window.py before emitting the signal
        self.show_login_window()
