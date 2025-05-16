from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QHBoxLayout, 
                          QSpacerItem, QSizePolicy, QGridLayout)
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QIcon, QPixmap, QColor
from functools import partial
from .styles import OLIVE, LIGHT_OLIVE, CREAM, PEACH, WINDOW_STYLE, TITLE_STYLE, SUBTITLE_STYLE, TEXT_STYLE

class TaskCard(QFrame):
    """Custom widget for task cards to create a more modern UI"""
    def __init__(self, task_name, hours, on_track_clicked):
        super().__init__()
        self.task_name = task_name
        self.hours = hours
        self.on_track_clicked = on_track_clicked
        self.init_ui()
    
    def init_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 12px;
                padding: 10px;
                box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
            }}
            QFrame:hover {{
                background-color: #F9F5E7;
                border: 1px solid {LIGHT_OLIVE};
                transform: translateY(-2px);
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Task info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        task_name = QLabel(self.task_name)
        task_name.setStyleSheet(f"color: {OLIVE}; font-weight: bold; font-size: 16px; letter-spacing: 0.3px;")
        
        hours_label = QLabel(f"{self.hours} hours")
        hours_label.setStyleSheet(f"color: {OLIVE}; font-size: 14px;")
        
        info_layout.addWidget(task_name)
        info_layout.addWidget(hours_label)
        
        # Track button
        track_btn = QPushButton('Track')
        track_btn.setFixedSize(100, 38)
        track_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        track_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PEACH};
                color: {OLIVE};
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background-color: {LIGHT_OLIVE};
                color: white;
                transform: scale(1.05);
            }}
            QPushButton:pressed {{
                background-color: {OLIVE};
                color: white;
            }}
        """)
        track_btn.clicked.connect(self.on_track_clicked)
        
        layout.addLayout(info_layout, 1)
        layout.addWidget(track_btn)
        
        self.setLayout(layout)

class ProjectCard(QFrame):
    """Custom widget for project cards with modern styling"""
    def __init__(self, project, on_task_clicked):
        super().__init__()
        self.project = project
        self.on_task_clicked = on_task_clicked
        self.init_ui()
    
    def init_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {LIGHT_OLIVE};
                border-radius: 16px;
                padding: 5px;
                box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.15);
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Project header with icon
        header_layout = QHBoxLayout()
        project_title = QLabel(self.project['name'])
        project_title.setStyleSheet(f"""
            font-size: 22px;
            font-weight: bold;
            color: {OLIVE};
            letter-spacing: 0.5px;
        """)
        
        header_layout.addWidget(project_title)
        header_layout.addStretch(1)
        
        layout.addLayout(header_layout)
        
        # Tasks
        for task in self.project['tasks']:
            task_card = TaskCard(
                task['name'], 
                task['hours'],
                partial(self.on_task_clicked, self.project, task)
            )
            layout.addWidget(task_card)
        
        self.setLayout(layout)

class DashboardWindow(QWidget):
    task_clicked = Signal(dict)

    def __init__(self, projects=None):
        super().__init__()
        self.projects = projects if projects else self.dummy_projects()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Time Tracker - Dashboard')
        self.setStyleSheet(WINDOW_STYLE)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(0, 0, 0, 20)

        # Header Bar with shadow effect
        header = QFrame()
        header.setStyleSheet(f"""
            background: {OLIVE}; 
            border-bottom-left-radius: 20px; 
            border-bottom-right-radius: 20px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
        """)
        header.setMinimumHeight(80)
        
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(30, 15, 30, 15)
        
        logo = QLabel("🕒 Time Tracker")
        logo.setStyleSheet(f"""
            color: {CREAM}; 
            font-size: 28px; 
            font-weight: bold;
            letter-spacing: 0.8px;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
        """)
        header_layout.addWidget(logo)
        header_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        user = QLabel("👤 User")
        user.setStyleSheet(f"""
            color: {CREAM}; 
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
        title = QLabel('My Projects')
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
        underline.setStyleSheet(f"background-color: {LIGHT_OLIVE}; min-height: 3px; max-height: 3px; border-radius: 1px; margin-left: 200px; margin-right: 200px;")
        
        title_container.addWidget(title)
        title_container.addWidget(underline)
        title_container.addSpacing(10)
        main_layout.addLayout(title_container)

        # Project Cards Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"border: none; background-color: transparent;")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setSpacing(20)
        scroll_layout.setContentsMargins(30, 10, 30, 30)

        # Add project cards
        for project in self.projects:
            project_card = ProjectCard(project, self.handle_task_click)
            scroll_layout.addWidget(project_card)
        
        # Add some space at the bottom
        scroll_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)

    def handle_task_click(self, project, task):
        self.task_clicked.emit({
            'project': project['name'],
            'task': task['name']
        })

    def dummy_projects(self):
        # Dummy data for demonstration
        return [
            {
                'name': 'Project A', 
                'tasks': [
                    {'name': 'Design User Interface', 'hours': 3.5},
                    {'name': 'Develop Frontend', 'hours': 5.0},
                    {'name': 'Backend Integration', 'hours': 2.5},
                ]
            },
            {
                'name': 'Project B', 
                'tasks': [
                    {'name': 'QA Testing', 'hours': 2.0},
                    {'name': 'Documentation', 'hours': 1.5},
                    {'name': 'Client Presentation', 'hours': 1.0},
                ]
            },
            {
                'name': 'Project C', 
                'tasks': [
                    {'name': 'Research', 'hours': 4.0},
                    {'name': 'Data Analysis', 'hours': 3.0},
                ]
            }
        ]
