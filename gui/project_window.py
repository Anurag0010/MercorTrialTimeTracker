from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QComboBox, QPushButton, QFrame, QSpacerItem, QSizePolicy,
                               QMessageBox)
from PySide6.QtCore import Signal, Qt
from .styles import WINDOW_STYLE, TITLE_STYLE, SUBTITLE_STYLE, TEXT_STYLE, OLIVE, LIGHT_OLIVE, CREAM, PEACH
from .api_service import APIService

class  ProjectWindow(QWidget):
    task_selected = Signal(dict)  # Emits {'project': ..., 'task': ...}

    def __init__(self, api_service=None):
        super().__init__()
        self.projects = []  # List of projects, each with tasks
        self.api_service = api_service or APIService.get_instance()
        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        self.setWindowTitle('Time Tracker – Project Selection')
        self.setGeometry(300, 300, 520, 350)
        self.setStyleSheet(WINDOW_STYLE)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(24)
        main_layout.setContentsMargins(38, 38, 38, 38)

        # Title
        title = QLabel('Select Project & Task')
        title.setStyleSheet(TITLE_STYLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        main_layout.addSpacing(10)

        # Selection container
        from .styles import CARD_STYLE, PRIMARY, ACCENT, TEXT_STYLE
        selection_frame = QFrame()
        selection_frame.setStyleSheet(CARD_STYLE)
        selection_layout = QVBoxLayout()
        selection_layout.setSpacing(18)
        selection_layout.setContentsMargins(26, 26, 26, 26)

        # Project selection
        project_layout = QHBoxLayout()
        self.project_label = QLabel('Project:')
        self.project_label.setStyleSheet(f"color: {PRIMARY}; font-size: 18px; font-weight: 700; letter-spacing: 0.5px;")
        self.project_combo = QComboBox()
        self.project_combo.setMinimumHeight(44)
        self.project_combo.setStyleSheet('font-size: 16px; font-weight: 500;')
        self.project_combo.currentIndexChanged.connect(self.on_project_changed)
        project_layout.addWidget(self.project_label)
        project_layout.addWidget(self.project_combo, 1)
        selection_layout.addLayout(project_layout)

        # Task selection
        task_layout = QHBoxLayout()
        self.task_label = QLabel('Task:')
        self.task_label.setStyleSheet(f"color: {PRIMARY}; font-size: 18px; font-weight: 700; letter-spacing: 0.5px;")
        self.task_combo = QComboBox()
        self.task_combo.setMinimumHeight(44)
        self.task_combo.setStyleSheet('font-size: 16px; font-weight: 500;')
        task_layout.addWidget(self.task_label)
        task_layout.addWidget(self.task_combo, 1)
        selection_layout.addLayout(task_layout)

        selection_frame.setLayout(selection_layout)
        main_layout.addWidget(selection_frame)
        main_layout.addSpacing(18)

        # Start button
        self.start_button = QPushButton('Start Tracking')
        self.start_button.setFixedHeight(46)
        self.start_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {PEACH};
                color: {OLIVE};
                border: none;
                border-radius: 12px;
                padding: 12px;
                font-weight: bold;
                font-size: 18px;
                letter-spacing: 0.8px;
                min-height: 50px;
            }}
            QPushButton:hover {{
                background-color: {LIGHT_OLIVE};
                color: white;
                transform: scale(1.03);
            }}
            QPushButton:pressed {{
                background-color: {OLIVE};
                color: white;
            }}
        """)
        self.task_combo.currentIndexChanged.connect(self.on_task_selected)
        # self.start_button.clicked.connect(self.handle_start)  # No longer needed for starting
        main_layout.addWidget(self.start_button)
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setLayout(main_layout)

    def setup_connections(self):
        """Set up signal/slot connections for API service"""
        self.api_service.projects_and_tasks_loaded.connect(self.on_projects_and_tasks_loaded)
        self.api_service.projects_and_tasks_error.connect(self.on_projects_and_tasks_error)
        
    def on_projects_loaded(self, projects):
        """Handler for when projects are loaded successfully"""
        self.projects = projects
        
        if not projects:
            QMessageBox.information(self, 'No Projects', 'No projects available. Please contact your administrator.')
            return
            
        for project in projects:
            self.project_combo.addItem(project['name'], project['id'])
            
        # Enable start button again
        self.start_button.setEnabled(True)
        
        # Load tasks for the first project
        self.load_tasks()

    def on_projects_and_tasks_loaded(self, projects_with_tasks):
        """Handle loaded projects and their tasks (single API call)."""
        self.projects = projects_with_tasks
        self.project_combo.clear()
        for project in self.projects:
            self.project_combo.addItem(project['name'], project['id'])
        if self.projects:
            self.load_tasks_for_project(self.projects[0]['id'])

    def on_projects_and_tasks_error(self, error_msg):
        QMessageBox.warning(self, 'Error', error_msg)

    def load_tasks_for_project(self, project_id):
        """Populate tasks for the selected project from already fetched data."""
        self.task_combo.clear()
        selected_project = next((p for p in self.projects if p['id'] == project_id), None)
        if selected_project and 'tasks' in selected_project:
            for task in selected_project['tasks']:
                self.task_combo.addItem(task['name'], task['id'])
        self.start_button.setEnabled(True)

    def on_project_changed(self, index):
        if index < 0 or index >= len(self.projects):
            return
        project_id = self.project_combo.itemData(index)
        self.load_tasks_for_project(project_id)
        # Optionally, auto-select the first task when project changes
        if self.task_combo.count() > 0:
            self.task_combo.setCurrentIndex(0)

    def on_task_selected(self, task_index):
        if task_index < 0 or self.project_combo.currentIndex() < 0:
            return
        project_index = self.project_combo.currentIndex()
        project = self.projects[project_index]
        if not project or 'tasks' not in project or task_index >= len(project['tasks']):
            return
        task = project['tasks'][task_index]
        # Emit signal with both project and task info
        self.task_selected.emit({'project': project, 'task': task})
        
        # Get current project ID
        project_id = self.project_combo.currentData()
        self.api_service.get_tasks(project_id)
        
    def on_tasks_loaded(self, tasks):
        """Handler for when tasks are loaded successfully"""
        self.tasks = tasks
        
        if not tasks:
            QMessageBox.information(self, 'No Tasks', 'No tasks available for this project.')
            return
            
        for task in tasks:
            self.task_combo.addItem(task['name'], task['id'])
            
        # Enable start button again
        self.start_button.setEnabled(True)

    def on_api_error(self, error_msg):
        """Handler for API errors"""
        QMessageBox.warning(self, 'Error', error_msg)
        self.start_button.setEnabled(True)

    def handle_start(self):
        """Handler for start button click"""
        if self.project_combo.count() == 0 or self.task_combo.count() == 0:
            QMessageBox.warning(self, 'Error', 'Please select both a project and a task.')
            return
            
        project_index = self.project_combo.currentIndex()
        task_index = self.task_combo.currentIndex()
        
        if project_index < 0 or task_index < 0:
            QMessageBox.warning(self, 'Error', 'Please select both a project and a task.')
            return
        
        project_id = self.project_combo.currentData()
        task_id = self.task_combo.currentData()
        
        selected_data = {
            'project_id': project_id,
            'project_name': self.project_combo.currentText(),
            'task_id': task_id,
            'task_name': self.task_combo.currentText()
        }
        
        self.task_selected.emit(selected_data)
