import requests
import json
import base64
import time
import functools
from PySide6.QtCore import QObject, Signal
from .constants import BASE_URL
from utils.network_utils import get_mac_address, get_ip_address
from utils.screenshot_utils import capture_screenshot
from utils.screenshot_utils import check_screenshot_permission
import os

import threading

class APIService(QObject):
    """Service to handle all API interactions with the backend (Singleton)"""
    
    # Define signals for API responses
    auth_success = Signal(dict)
    auth_error = Signal(str)
    logout_success = Signal()
    logout_error = Signal(str)
    token_expired = Signal()  # Signal when refresh token has expired
    projects_loaded = Signal(list)
    projects_error = Signal(str)
    tasks_loaded = Signal(list)
    tasks_error = Signal(str)
    projects_and_tasks_loaded = Signal(list)  # List of projects, each with their tasks
    projects_and_tasks_error = Signal(str)
    timelog_posted = Signal(bool)
    timelog_error = Signal(str)
    screenshot_posted = Signal(bool)
    screenshot_error = Signal(str)

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        super().__init__()
        self.access_token = None
        self.refresh_token = None
        self.user_id = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def requires_auth(error_signal_name=None):
        """
        Decorator that ensures a method is only called when authenticated.
        
        Args:
            error_signal_name: Name of the signal to emit if authentication fails
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                if not self._ensure_authenticated():
                    # Find and emit the appropriate error signal if provided
                    if error_signal_name and hasattr(self, error_signal_name):
                        error_signal = getattr(self, error_signal_name)
                        error_signal.emit("Not authenticated")
                    return None if not kwargs.get('return_on_error') else kwargs.get('return_on_error')
                return func(self, *args, **kwargs)
            return wrapper
        return decorator
    
    def authenticate(self, username, password, mac_address):
        """Authenticate user with the backend API (OpenAPI: POST /api/auth/employee/login)"""
        try:
            url = f"{BASE_URL}/api/auth/employee/login"
            payload = {
                "email": username,
                "password": password,
                "mac_address": mac_address
            }
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                # Store tokens and user_id as per OpenAPI Token schema
                self.access_token = data.get('access_token')
                self.refresh_token = data.get('refresh_token')
                self.user_id = data.get('employee_id') or data.get('user_id')
                print("[APIService] Emitting auth_success with data:", data)
                self.auth_success.emit(data)
                return True
            else:
                try:
                    error_msg = response.json().get('message', 'Authentication failed')
                except Exception:
                    error_msg = 'Authentication failed'
                print("[APIService] Emitting auth_error with message:", error_msg)
                self.auth_error.emit(error_msg)
                return False
        except Exception as e:
            print("[APIService] Emitting auth_error with exception:", str(e))
            self.auth_error.emit(f"Error connecting to server: {str(e)}")
            return False
    
    def refresh_access_token(self):
        """Refresh the access token using refresh token (OpenAPI: POST /api/auth/refresh)"""
        try:
            url = f"{BASE_URL}/api/auth/refresh"
            payload = {
                "refresh_token": self.refresh_token
            }
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                return True
            else:
                self.token_expired.emit()
                return False
        except Exception:
            self.token_expired.emit()
            return False
    
    def logout(self):
        """Log out user and invalidate tokens (OpenAPI: POST /api/auth/logout if present)"""
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
        self.logout_success.emit()
        return True
    
    @requires_auth(error_signal_name="projects_error")
    def get_projects_and_tasks(self):
        """Fetch all projects and their tasks for the authenticated employee (GET /api/employees/projects)"""
        try:
            url = f"{BASE_URL}/api/employees/tasks"
            headers = self._get_auth_headers()
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.projects_and_tasks_loaded.emit(data)
                return data
            elif response.status_code == 401:
                if self._handle_token_expiry():
                    return self.get_projects_and_tasks()
                return None
            else:
                try:
                    error_msg = response.json().get('message', 'Failed to fetch projects and tasks')
                except Exception:
                    error_msg = 'Failed to fetch projects and tasks'
                self.projects_and_tasks_error.emit(error_msg)
                return None
        except Exception as e:
            self.projects_and_tasks_error.emit(f"Error fetching projects and tasks: {str(e)}")
            return None
    
    @requires_auth(error_signal_name="tasks_error")
    def get_tasks(self, project_id=None):
        """Fetch tasks for a specific project (OpenAPI: GET /api/projects/{project_id}/tasks)"""
        try:
            if not project_id:
                self.tasks_error.emit("No project selected")
                return None
            url = f"{BASE_URL}/api/employees/projects"
            headers = self._get_auth_headers()
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.tasks_loaded.emit(data)
                return data
            elif response.status_code == 401:
                if self._handle_token_expiry():
                    return self.get_tasks(project_id)
                return None
            else:
                try:
                    error_msg = response.json().get('message', 'Failed to fetch tasks')
                except Exception:
                    error_msg = 'Failed to fetch tasks'
                self.tasks_error.emit(error_msg)
                return None
        except Exception as e:
            self.tasks_error.emit(f"Error fetching tasks: {str(e)}")
            return None
    
    @requires_auth(error_signal_name="timelog_error")
    def post_timelog_with_screenshot(self, task_id, project_id, start_time, end_time, duration):
        """
        Post time tracking information and screenshot to the backend in a single API call.
        Uses multipart/form-data as per OpenAPI/Swagger definition.
        """
        # convert start and end_time to epoch time if not already
        if isinstance(start_time, str):
            start_time = int(time.mktime(time.strptime(start_time, '%Y-%m-%dT%H:%M:%S.%f')))
        if isinstance(end_time, str):
            end_time = int(time.mktime(time.strptime(end_time, '%Y-%m-%dT%H:%M:%S.%f')))
        if isinstance(duration, str):
            duration = int(duration)
        if isinstance(duration, float):
            duration = int(duration)    
        try:
            url = f"{BASE_URL}/api/timelogs"

            # 2. Check screenshot permission
            is_screenshot_permission_enabled = check_screenshot_permission()

            if is_screenshot_permission_enabled:
                # 1. Capture screenshot
                screenshot_path = capture_screenshot()
                if not screenshot_path or not os.path.exists(screenshot_path):
                    self.timelog_error.emit("Failed to capture screenshot.")
                    return False
            
            # 3. Get network info
            mac_addresses = get_mac_address()
            mac_address = mac_addresses.get("primary", "")
            ip_addresses = get_ip_address()
            ip_address = ip_addresses.get("primary", "")

            # 4. Prepare multipart/form-data payload
            files = {
                'file': open(screenshot_path, 'rb')
            }
            data = {
                'task_id': task_id,
                'project_id': project_id,
                'start_time': start_time,
                'end_time': end_time,
                'duration': duration,
                'is_screenshot_permission_enabled': str(is_screenshot_permission_enabled),
                'ip_address': ip_address,
                'mac_address': mac_address
            }
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            response = requests.post(url, data=data, files=files, headers=headers)

            # 5. Clean up screenshot file
            try:
                files['file'].close()
                os.remove(screenshot_path)
            except Exception:
                pass

            if response.status_code in [200, 201]:
                self.timelog_posted.emit(True)
                return True
            elif response.status_code == 401:
                if self._handle_token_expiry():
                    return self.post_timelog_with_screenshot(task_id, project_id, start_time, end_time, duration)
                return False
            else:
                try:
                    error_msg = response.json().get('message', 'Failed to post timelog with screenshot')
                except Exception:
                    error_msg = 'Failed to post timelog with screenshot'
                self.timelog_error.emit(error_msg)
                return False
        except Exception as e:
            self.timelog_error.emit(f"Error posting timelog with screenshot: {str(e)}")
            return False
    
    @requires_auth(error_signal_name=None)
    def check_screenshot_permission(self):
        """Send information about screenshot permission to the API"""
        try:
            url = f"{BASE_URL}/api/permissions/screenshot"
            
            # In a real app, you would actually check system permissions
            # This is a placeholder - you need to implement the actual permission check
            has_permission = True
            
            payload = {
                "user_id": self.user_id,
                "has_permission": has_permission
            }
            
            headers = self._get_auth_headers()
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code in [200, 201]:
                return True
            elif response.status_code == 401:
                # Token might have expired
                if self._handle_token_expiry():
                    # Retry the request
                    return self.check_screenshot_permission()
                return False
            else:
                return False
        except:
            return False
    
    def _get_auth_headers(self):
        """Helper method to get authorization headers"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def _ensure_authenticated(self):
        """Check if user is authenticated (access token present)"""
        return bool(self.access_token)

    
    def _handle_token_expiry(self):
        """Handle token expiry by refreshing or signaling"""
        # Always try to refresh the access token
        return self.refresh_access_token()