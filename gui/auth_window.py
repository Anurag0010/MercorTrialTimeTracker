from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QMessageBox)
from PySide6.QtCore import Signal, Qt
from .styles import WINDOW_STYLE, TITLE_STYLE, TEXT_STYLE
from .api_service import APIService
from utils.network_utils import get_mac_address
class AuthWindow(QWidget):
    login_successful = Signal()

    def __init__(self, api_service=None):
        super().__init__()
        self.api_service = api_service or APIService.get_instance()
        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        self.setWindowTitle('Time Tracker – Login')
        self.setGeometry(300, 300, 420, 340)
        self.setStyleSheet(WINDOW_STYLE)

        layout = QVBoxLayout()
        layout.setSpacing(22)
        layout.setContentsMargins(38, 38, 38, 38)

        # Title
        title = QLabel('Welcome Back!')
        title.setStyleSheet(TITLE_STYLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Username
        self.username_label = QLabel('Username')
        self.username_label.setStyleSheet(TEXT_STYLE)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Enter your username')
        self.username_input.setMinimumHeight(44)
        self.username_input.setStyleSheet('''
            QLineEdit {
                background: white;
                border: 2px solid #e5e7eb;
                border-radius: 10px;
                padding: 12px 16px;
                font-size: 17px;
                color: #1E293B;
                font-family: 'Segoe UI', 'Inter', 'Arial', sans-serif;
                transition: border 0.2s, box-shadow 0.2s;
                box-shadow: 0 1px 4px 0 rgba(30,64,175,0.06);
            }
            QLineEdit:focus {
                border: 2px solid #1E40AF;
                box-shadow: 0 2px 8px 0 rgba(30,64,175,0.13);
                outline: none;
            }
            QLineEdit::placeholder {
                color: #94A3B8;
                font-size: 16px;
            }
        ''')
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)

        # Password
        self.password_label = QLabel('Password')
        self.password_label.setStyleSheet(TEXT_STYLE)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Enter your password')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(44)
        self.password_input.setStyleSheet('''
            QLineEdit {
                background: white;
                border: 2px solid #e5e7eb;
                border-radius: 10px;
                padding: 12px 16px;
                font-size: 17px;
                color: #1E293B;
                font-family: 'Segoe UI', 'Inter', 'Arial', sans-serif;
                transition: border 0.2s, box-shadow 0.2s;
                box-shadow: 0 1px 4px 0 rgba(30,64,175,0.06);
            }
            QLineEdit:focus {
                border: 2px solid #1E40AF;
                box-shadow: 0 2px 8px 0 rgba(30,64,175,0.13);
                outline: none;
            }
            QLineEdit::placeholder {
                color: #94A3B8;
                font-size: 16px;
            }
        ''')
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        # Add some spacing
        layout.addSpacing(24)

        # Login button
        self.login_button = QPushButton('Login')
        self.login_button.setFixedHeight(46)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.setStyleSheet('font-size: 18px; font-weight: 700;')
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)
        
    def setup_connections(self):
        """Set up signal/slot connections for API service"""
        self.api_service.auth_success.connect(self.on_auth_success)
        self.api_service.auth_error.connect(self.on_auth_error)
        
        # Enter key in password field should trigger login
        self.password_input.returnPressed.connect(self.handle_login)

    def handle_login(self):
        """Handler for login button click"""
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, 'Error', 'Please enter both username and password')
            return
            
        # Show loading state
        self.login_button.setEnabled(False)
        self.login_button.setText('Logging in...')
        
        # get mac address from the utils
        mac_address = get_mac_address()
        
        primary_mac_address = mac_address.get('primary', '')
        
        # Call the API service for authentication
        self.api_service.authenticate(username, password, primary_mac_address)
    
    def on_auth_success(self, data):
        """Handler for successful authentication"""
        self.login_button.setEnabled(True)
        self.login_button.setText('Login')
        # Signal to main app that login was successful
        self.login_successful.emit()
    
    def on_auth_error(self, error_msg):
        """Handler for authentication error"""
        self.login_button.setEnabled(True)
        self.login_button.setText('Login')
        QMessageBox.warning(self, 'Login Failed', error_msg)
