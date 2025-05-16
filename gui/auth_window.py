from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QMessageBox)
from PySide6.QtCore import Signal, Qt
from .styles import WINDOW_STYLE, TITLE_STYLE, TEXT_STYLE

class AuthWindow(QWidget):
    login_successful = Signal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Time Tracker - Login')
        self.setGeometry(300, 300, 400, 300)
        self.setStyleSheet(WINDOW_STYLE)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = QLabel('Welcome Back')
        title.setStyleSheet(TITLE_STYLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Username
        self.username_label = QLabel('Username')
        self.username_label.setStyleSheet(TEXT_STYLE)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Enter your username')
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)

        # Password
        self.password_label = QLabel('Password')
        self.password_label.setStyleSheet(TEXT_STYLE)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Enter your password')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        # Add some spacing
        layout.addSpacing(20)

        # Login button
        self.login_button = QPushButton('Login')
        self.login_button.setFixedHeight(40)
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # TODO: Replace with actual API call
        if username and password:  # Dummy authentication
            self.login_successful.emit()
        else:
            QMessageBox.warning(self, 'Error', 'Invalid credentials')
