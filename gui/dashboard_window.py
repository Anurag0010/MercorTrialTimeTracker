from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QHBoxLayout, 
                          QSpacerItem, QSizePolicy, QGridLayout)
from PySide6.QtCore import Signal, Qt
from functools import partial
from .styles import OLIVE, WINDOW_STYLE, TITLE_STYLE, SUBTITLE_STYLE, TEXT_STYLE, PRIMARY, SECONDARY, TERTIARY, DARK_PRIMARY, LIGHT_PRIMARY, SUCCESS, WARNING, DANGER, INFO, WHITE, GRAY, DARK_GRAY, BLACK, CARD_STYLE, SHADOW
from .api_service import APIService

class TaskCard(QFrame):
    """Custom widget for task cards to create a more modern UI"""
    def __init__(self, task_data, on_track_clicked):
        super().__init__()
        self.task_data = task_data
        self.on_track_clicked = on_track_clicked
        self.init_ui()
    
    def init_ui(self):
        from .styles import CARD_STYLE, PRIMARY, TEXT_STYLE
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {WHITE};
                border-radius: 12px;
                border: 1px solid {LIGHT_PRIMARY};
                box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.08);
            }}
            QFrame:hover {{
                border: 1px solid {PRIMARY};
                background-color: rgba(224, 231, 255, 0.2);
            }}
        """)
        layout = QHBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 12, 16, 12)

        # Task info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        # Display task name
        task_name = self.task_data.get('name', 'Unnamed Task')
        task_label = QLabel(f"Task: {task_name}")
        task_label.setStyleSheet(f"color: {PRIMARY}; font-weight: 700; font-size: 16px; letter-spacing: 0.3px;")
        
        # Time container
        time_container = QHBoxLayout()
        time_container.setSpacing(2)
        
        # Display hours if available or default to 0
        mins = self.task_data.get('task_spent_time_in_minutes_real', 0)
        
        # Make sure mins is a whole number integer
        if isinstance(mins, float):
            mins = int(mins)
        
        # Format as HH:mm with whole numbers
        hours = mins // 60
        minutes = mins % 60
        time_icon = QLabel("🕒")
        time_icon.setStyleSheet(f"font-size: 12px; margin-right: 4px;")
        time_label = QLabel(f"{int(hours):02d}:{int(minutes):02d}")
        time_label.setStyleSheet(f"""
            color: {SECONDARY}; 
            font-size: 13px; 
            font-weight: 500;
            background-color: rgba(224, 231, 255, 0.4);
            border-radius: 6px;
            padding: 2px 6px;
        """)
        
        time_container.addWidget(time_icon)
        time_container.addWidget(time_label)
        time_container.addStretch()
        
        info_layout.addWidget(task_label)
        info_layout.addLayout(time_container)

        # Track button
        track_btn = QPushButton('Start')
        track_btn.setFixedSize(70, 32)
        track_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        track_btn.setStyleSheet(f'''
            QPushButton {{
                background-color: {PRIMARY};
                color: {WHITE};
                border: none;
                border-radius: 6px;
                padding: 4px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {DARK_PRIMARY};
                transform: translateY(-1px);
            }}
            QPushButton:pressed {{
                background-color: {DARK_PRIMARY};
                transform: translateY(1px);
            }}
        ''')
        track_btn.clicked.connect(self.on_track_clicked)

        layout.addLayout(info_layout, 1)
        layout.addWidget(track_btn)
        self.setLayout(layout)

class ProjectTaskCard(QFrame):
    """Custom widget for project cards with modern styling"""
    def __init__(self, project_task_data, on_task_clicked):
        super().__init__()
        self.project_task_data = project_task_data
        self.on_task_clicked = on_task_clicked
        self.init_ui()
    
    def init_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {WHITE};
                border-radius: 16px;
                border: 1px solid rgba(99, 102, 241, 0.1);
                box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.08);
            }}
            QFrame:hover {{
                box-shadow: 0px 6px 16px rgba(0, 0, 0, 0.12);
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Project header with icon
        header_layout = QHBoxLayout()
        
        # Project icon
        icon_label = QLabel("📂")
        icon_label.setStyleSheet("font-size: 20px; margin-right: 8px;")
        
        # Get project name or use 'Unnamed Project' as fallback
        project_name = self.project_task_data[0]
        project_title = QLabel(f"Project: {project_name}")
        project_title.setStyleSheet(f"""
            font-size: 20px;
            font-weight: 800;
            color: {PRIMARY};
            letter-spacing: 0.5px;
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(project_title)
        header_layout.addStretch(1)
        
        # Add task count badge
        tasks = self.project_task_data[1]
        task_count = len(tasks) if tasks else 0
        task_count_label = QLabel(f"{task_count} task{'s' if task_count != 1 else ''}")
        task_count_label.setStyleSheet(f"""
            background-color: {LIGHT_PRIMARY};
            color: {PRIMARY};
            border-radius: 10px;
            padding: 4px 10px;
            font-size: 13px;
            font-weight: 600;
        """)
        header_layout.addWidget(task_count_label)
        
        layout.addLayout(header_layout)
        
        # Add separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: rgba(99, 102, 241, 0.1); margin: 4px 0px 8px 0px; min-height: 1px; max-height: 1px;")
        layout.addWidget(separator)
        
        # Tasks
        if tasks:
            tasks_container = QVBoxLayout()
            tasks_container.setSpacing(8)
            
            for task in tasks:
                task_card = TaskCard(
                    task, 
                    partial(self.on_task_clicked, self.project_task_data, task)
                )
                tasks_container.addWidget(task_card)
                
            layout.addLayout(tasks_container)
        else:
            # Show message if no tasks
            no_tasks = QLabel("No tasks assigned to this project")
            no_tasks.setStyleSheet(f"color: {DARK_GRAY}; font-style: italic; padding: 10px;")
            no_tasks.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(no_tasks)
        
        self.setLayout(layout)

class DashboardWindow(QWidget):
    task_clicked = Signal(dict)

    def __init__(self, projects=None, api_service=None):
        super().__init__()
        self.api_service = api_service or APIService.get_instance()
        self.tasks = projects or []
        self.init_ui()
        self.setup_connections()

    def setup_connections(self):
        """Set up signal connections for API service"""
        # Connect signals from API service
        self.api_service.projects_and_tasks_loaded.connect(self.update_tasks)
        self.api_service.projects_and_tasks_error.connect(self.handle_api_error)

    def init_ui(self):
        self.setWindowTitle('Time Tracker - Dashboard')
        self.setStyleSheet(WINDOW_STYLE)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(0, 0, 0, 20)

        # Header Bar with shadow effect
        header = QFrame()
        header.setStyleSheet(f"""
            background: {LIGHT_PRIMARY}; 
            border-bottom-left-radius: 20px; 
            border-bottom-right-radius: 20px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
        """)
        header.setMinimumHeight(80)
        
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(30, 15, 30, 15)
        
        logo = QLabel("🕒 Time Tracker")
        logo.setStyleSheet(f"""
            color: {PRIMARY}; 
            font-size: 28px; 
            font-weight: bold;
            letter-spacing: 0.8px;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
        """)
        header_layout.addWidget(logo)
        header_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        user = QLabel("👤 User")
        user.setStyleSheet(f"""
            color: {PRIMARY}; 
            font-size: 18px;
            background-color: rgba(255, 255, 255, 0.2);
            padding: 6px 12px;
            border-radius: 15px;
        """)
        header_layout.addWidget(user)
        
        header.setLayout(header_layout)
        main_layout.addWidget(header)

        # Title with decorative underline
        title_container = QVBoxLayout()
        title = QLabel('My Tasks')
        title.setStyleSheet(f"""
            {TITLE_STYLE}
            padding-bottom: 5px;
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.1);
            letter-spacing: 0.8px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add decorative line under title
        underline = QFrame()
        underline.setFrameShape(QFrame.Shape.HLine)
        underline.setStyleSheet(f"background-color: {WHITE}; min-height: 3px; max-height: 3px; border-radius: 1px; margin-left: 200px; margin-right: 200px;")
        
        title_container.addWidget(title)
        title_container.addWidget(underline)
        title_container.addSpacing(10)
        main_layout.addLayout(title_container)

        # Project Cards Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet(f"border: none; background-color: transparent;")
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setSpacing(20)
        self.scroll_layout.setContentsMargins(30, 10, 30, 30)

        # Add loading message initially
        self.loading_label = QLabel("Loading tasks...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet(f"color: {OLIVE}; font-size: 18px; margin: 50px 0;")
        self.scroll_layout.addWidget(self.loading_label)
        
        # Add some space at the bottom
        self.scroll_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        self.scroll_content.setLayout(self.scroll_layout)
        self.scroll.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll)
        
        self.setLayout(main_layout)

    def handle_task_click(self, task_proj_tuple, task):
        """Handle when a task card is clicked"""
        print(f"Task clicked: {task}")
        print(f"Project: {task_proj_tuple}")
        task_data = {
            'project_id': task.get('project_id'),
            'project_name': task.get('project_name'),
            'task_id': task.get('id'),
            'task_name': task.get('name', 'Unknown Task')
        }
        print(f"Task clicked: {task_data}")
        self.task_clicked.emit(task_data)

    def update_tasks(self, tasks):
        """Update the dashboard with the real projects and tasks data from API"""
        print(f"Updating dashboard with {len(tasks)} tasks")
        self.tasks = tasks
        
        # Clear existing widgets
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        
        if not tasks:
            # Show message if no projects/tasks
            no_tasks = QLabel("No tasks assigned to you")
            no_tasks.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_tasks.setStyleSheet(f"color: {OLIVE}; font-size: 18px; margin: 50px 0;")
            self.scroll_layout.addWidget(no_tasks)
        else:
            # Add project cards with real data
            proj_ts = {}
            for t in tasks:
                project_name = t.get('project_name', 'Unnamed Project')
                if project_name not in proj_ts:
                    proj_ts[project_name] = []
                proj_ts[project_name].append(t)
                
            for project, ts in proj_ts.items():
                # Create a project card with the tasks
                project_card = ProjectTaskCard((project, ts), self.handle_task_click)
                self.scroll_layout.addWidget(project_card)
        
        # Add spacer at the bottom
        self.scroll_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def handle_api_error(self, error_msg):
        """Handle API errors"""
        # Show error message
        error_label = QLabel(f"Error loading tasks: {error_msg}")
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_label.setStyleSheet("color: red; font-size: 16px; margin: 50px 0;")
        
        # Clear existing widgets
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
                
        self.scroll_layout.addWidget(error_label)
        self.scroll_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def update_projects(self, projects):
        """Update the dashboard with projects data - alias for update_tasks for compatibility"""
        self.update_tasks(projects)

    def dummy_projects(self):
        # Dummy data for demonstration
        return [
            {
                'name': 'Project A', 
                'tasks': [
                    {'name': 'Design User Interface', 'estimated_hours': 3.5},
                    {'name': 'Develop Frontend', 'estimated_hours': 5.0},
                    {'name': 'Backend Integration', 'estimated_hours': 2.5},
                ]
            },
            {
                'name': 'Project B', 
                'tasks': [
                    {'name': 'QA Testing', 'estimated_hours': 2.0},
                    {'name': 'Documentation', 'estimated_hours': 1.5},
                    {'name': 'Client Presentation', 'estimated_hours': 1.0},
                ]
            },
            {
                'name': 'Project C', 
                'tasks': [
                    {'name': 'Research', 'estimated_hours': 4.0},
                    {'name': 'Data Analysis', 'estimated_hours': 3.0},
                ]
            }
        ]
