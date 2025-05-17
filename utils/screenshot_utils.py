"""
Utility module for capturing screenshots.
Provides functions to capture screenshots across different platforms.
"""

import os
import time
from datetime import datetime
import mss
import mss.tools
from PIL import Image

def capture_screenshot(output_dir="screenshots", filename=None):
    """
    Capture a screenshot of all monitors and save it to the specified directory.
    
    Args:
        output_dir (str): Directory where the screenshot will be saved
        filename (str, optional): Filename for the screenshot. If not provided, 
                                a timestamp-based name will be generated.
                                
    Returns:
        str: Path to the saved screenshot file
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
    
    # Ensure file has .png extension
    if not filename.lower().endswith('.png'):
        filename += '.png'
    
    filepath = os.path.join(output_dir, filename)
    
    # Capture screenshot using mss
    try:
        with mss.mss() as sct:
            # Capture all monitors by default
            monitor = sct.monitors[0]  # All monitors
            screenshot = sct.grab(monitor)
            mss.tools.to_png(screenshot.rgb, screenshot.size, output=filepath)
            return filepath
    except Exception as e:
        print(f"Error capturing screenshot: {str(e)}")
        return None

def capture_specific_monitor(monitor_number=1, output_dir="screenshots", filename=None):
    """
    Capture a screenshot of a specific monitor and save it to the specified directory.
    
    Args:
        monitor_number (int): The monitor number to capture (1-based indexing)
        output_dir (str): Directory where the screenshot will be saved
        filename (str, optional): Filename for the screenshot. If not provided, 
                                a timestamp-based name will be generated.
                                
    Returns:
        str: Path to the saved screenshot file
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_monitor{monitor_number}_{timestamp}.png"
    
    # Ensure file has .png extension
    if not filename.lower().endswith('.png'):
        filename += '.png'
    
    filepath = os.path.join(output_dir, filename)
    
    # Capture screenshot using mss
    try:
        with mss.mss() as sct:
            # Adjust monitor number (mss uses 0-based indexing, but we use 1-based for user-friendliness)
            monitor_idx = min(monitor_number, len(sct.monitors) - 1)
            if monitor_idx <= 0:
                monitor_idx = 1  # Default to first monitor
            
            # Capture specific monitor
            monitor = sct.monitors[monitor_idx]
            screenshot = sct.grab(monitor)
            mss.tools.to_png(screenshot.rgb, screenshot.size, output=filepath)
            return filepath
    except Exception as e:
        print(f"Error capturing screenshot of monitor {monitor_number}: {str(e)}")
        return None

def check_screenshot_permission():
    """
    Check if the application has permission to take screenshots.
    
    Returns:
        bool: True if screenshot permission is granted, False otherwise
    """
    try:
        with mss.mss() as sct:
            # Try to take a small screenshot to check permission
            monitor = sct.monitors[1]  # First monitor
            test_file = os.path.join("screenshots", "test_permission.png")
            test_dir = os.path.dirname(test_file)
            
            if not os.path.exists(test_dir):
                os.makedirs(test_dir)
                
            screenshot = sct.grab(monitor)
            mss.tools.to_png(screenshot.rgb, screenshot.size, output=test_file)
            
            # Clean up test file
            if os.path.exists(test_file):
                try:
                    os.remove(test_file)
                except:
                    pass
                    
            return True
    except Exception as e:
        print(f"Screenshot permission check failed: {str(e)}")
        return False

def compress_screenshot(screenshot_path, quality=70, max_retries=3):
    """
    Compress a screenshot to reduce file size.
    
    Args:
        screenshot_path (str): Path to the screenshot file to compress
        quality (int): JPEG quality (1-100, lower means more compression)
        max_retries (int): Maximum number of compression attempts if errors occur
        
    Returns:
        str: Path to the compressed screenshot file
    """
    if not os.path.exists(screenshot_path):
        print(f"Cannot compress - file not found: {screenshot_path}")
        return screenshot_path
        
    output_path = os.path.splitext(screenshot_path)[0] + "_compressed.jpg"
    
    # Try multiple times in case of file access issues
    for attempt in range(max_retries):
        try:
            # Open the original PNG screenshot
            img = Image.open(screenshot_path)
            
            # Create a compressed version with JPEG format
            img.convert('RGB').save(output_path, 'JPEG', quality=quality, optimize=True)
            
            # Verify the file was created successfully
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(f"Successfully compressed screenshot to {output_path}")
                return output_path
            else:
                print(f"Compression failed - output file is empty or not created")
                
        except PermissionError as pe:
            print(f"Permission error while compressing (attempt {attempt+1}/{max_retries}): {str(pe)}")
            time.sleep(0.5)  # Wait before retrying
        except IOError as ioe:
            print(f"IO error while compressing (attempt {attempt+1}/{max_retries}): {str(ioe)}")
            time.sleep(0.5)  # Wait before retrying
        except Exception as e:
            print(f"Error compressing screenshot (attempt {attempt+1}/{max_retries}): {str(e)}")
            time.sleep(0.3)  # Short delay before retry
    
    print(f"All compression attempts failed, returning original screenshot")
    return screenshot_path  # Return original path if all compression attempts fail

def get_monitor_info():
    """
    Get information about available monitors.
    
    Returns:
        list: List of dictionaries containing monitor information 
             (index, width, height, left, top)
    """
    try:
        with mss.mss() as sct:
            monitors = []
            # Monitor 0 is a special case that represents the entire virtual screen
            # So we start from index 1 for actual physical monitors
            for i, monitor in enumerate(sct.monitors[1:], 1):
                monitors.append({
                    'index': i,
                    'width': monitor['width'],
                    'height': monitor['height'],
                    'left': monitor['left'],
                    'top': monitor['top']
                })
            return monitors
    except Exception as e:
        print(f"Error getting monitor information: {str(e)}")
        # Return a fallback single monitor if detection fails
        return [{'index': 1, 'width': 1920, 'height': 1080, 'left': 0, 'top': 0}]