from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QComboBox, QPushButton, QFrame, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Signal, Qt
from .styles import WINDOW_STYLE, TITLE_STYLE, SUBTITLE_STYLE, TEXT_STYLE, OLIVE, LIGHT_OLIVE, CREAM, PEACH

class ProjectWindow(QWidget):
    task_selected = Signal(dict)

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_projects()

    def init_ui(self):
        self.setWindowTitle('Time Tracker - Project Selection')
        self.setGeometry(300, 300, 500, 300)
        self.setStyleSheet(WINDOW_STYLE)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = QLabel('Select Project & Task')
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
        underline.setStyleSheet(f"background-color: {LIGHT_OLIVE}; min-height: 3px; max-height: 3px; border-radius: 1px;")
        
        main_layout.addWidget(title)
        main_layout.addWidget(underline)
        main_layout.addSpacing(10)

        # Selection container
        selection_frame = QFrame()
        selection_frame.setStyleSheet(f"""
            background-color: {LIGHT_OLIVE};
            border-radius: 16px;
            padding: 10px;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.15);
        """)
        
        selection_layout = QVBoxLayout()
        selection_layout.setSpacing(15)
        selection_layout.setContentsMargins(20, 20, 20, 20)

        # Project selection
        project_layout = QHBoxLayout()
        self.project_label = QLabel('Project:')
        self.project_label.setStyleSheet(f"""
            color: {OLIVE};
            font-size: 18px;
            font-weight: bold;
            letter-spacing: 0.5px;
        """)
        
        self.project_combo = QComboBox()
        self.project_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: white;
                border: 2px solid {OLIVE};
                border-radius: 8px;
                padding: 8px;
                color: {OLIVE};
                font-size: 16px;
                min-height: 40px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox::down-arrow {{
                image: url(dropdown.png);
                width: 12px;
                height: 12px;
            }}
            QComboBox QAbstractItemView {{
                background-color: white;
                border: 2px solid {OLIVE};
                border-radius: 8px;
                selection-background-color: {LIGHT_OLIVE};
                selection-color: white;
            }}
        """)
        self.project_combo.currentIndexChanged.connect(self.load_tasks)
        project_layout.addWidget(self.project_label)
        project_layout.addWidget(self.project_combo, 1)
        selection_layout.addLayout(project_layout)

        # Task selection
        task_layout = QHBoxLayout()
        self.task_label = QLabel('Task:')
        self.task_label.setStyleSheet(f"""
            color: {OLIVE};
            font-size: 18px;
            font-weight: bold;
            letter-spacing: 0.5px;
        """)
        
        self.task_combo = QComboBox()
        self.task_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: white;
                border: 2px solid {OLIVE};
                border-radius: 8px;
                padding: 8px;
                color: {OLIVE};
                font-size: 16px;
                min-height: 40px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox::down-arrow {{
                image: url(dropdown.png);
                width: 12px;
                height: 12px;
            }}
            QComboBox QAbstractItemView {{
                background-color: white;
                border: 2px solid {OLIVE};
                border-radius: 8px;
                selection-background-color: {LIGHT_OLIVE};
                selection-color: white;
            }}
        """)
        task_layout.addWidget(self.task_label)
        task_layout.addWidget(self.task_combo, 1)
        selection_layout.addLayout(task_layout)
        
        selection_frame.setLayout(selection_layout)
        main_layout.addWidget(selection_frame)
        
        # Add some spacing
        main_layout.addSpacing(10)

        # Start button
        self.start_button = QPushButton('Start Timer')
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
        self.start_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_button.clicked.connect(self.handle_start)
        main_layout.addWidget(self.start_button)
        
        # Add spacer at the bottom
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setLayout(main_layout)

    def load_projects(self):
        # TODO: Replace with actual API call
        dummy_projects = ['Project A', 'Project B', 'Project C']
        self.project_combo.addItems(dummy_projects)

    def load_tasks(self):
        # TODO: Replace with actual API call
        project = self.project_combo.currentText()
        dummy_tasks = [f'{project} - Task 1', f'{project} - Task 2']
        
        self.task_combo.clear()
        self.task_combo.addItems(dummy_tasks)

    def handle_start(self):
        selected_data = {
            'project': self.project_combo.currentText(),
            'task': self.task_combo.currentText()
        }
        self.task_selected.emit(selected_data)
