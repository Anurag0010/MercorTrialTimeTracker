# This palette and style system is inspired by tailwind.config.ts (see root of project)
# All color values and design decisions are mapped from the Tailwind 'teamtrack' theme.
# If you update the Tailwind config, please mirror changes here for design consistency.

# Base Colors
WHITE = "#FFFFFF"
BLACK = "#000000"
GRAY = "#F5F7FA"
DARK_GRAY = "#CED4DA"

# Old blues (kept for backward compatibility)
OLD_DARK_BLUE = "#0A3177"
OLD_MEDIUM_BLUE = "#1E56A0"
OLD_LIGHT_BLUE = "#D6E4F0"

# Light Mode Color Palette
PRIMARY = "#6366F1"  # Indigo
SECONDARY = "#8B5CF6"  # Purple
TERTIARY = "#EC4899"  # Pink
SUCCESS = "#10B981"  # Green
WARNING = "#F59E0B"  # Amber
DANGER = "#EF4444"  # Red
INFO = "#3B82F6"  # Blue
OLIVE = "#84CC16"  # Olive/Lime green
DARK_PRIMARY = "#4F46E5"  # Darker Indigo
LIGHT_PRIMARY = "#E0E7FF"  # Light Indigo
LIGHT_BG = "#F9FAFB"  # Light background
LIGHT_TEXT = "#111827"  # Dark text for light mode

# Dark Mode Color Palette (new)
DARK_MODE_PRIMARY = "#818CF8"  # Brighter Indigo for dark mode
DARK_MODE_SECONDARY = "#A78BFA"  # Brighter Purple for dark mode
DARK_MODE_TERTIARY = "#F472B6"  # Brighter Pink for dark mode
DARK_MODE_SUCCESS = "#34D399"  # Brighter Green for dark mode
DARK_MODE_WARNING = "#FBBF24"  # Brighter Amber for dark mode
DARK_MODE_DANGER = "#F87171"  # Brighter Red for dark mode
DARK_MODE_INFO = "#60A5FA"  # Brighter Blue for dark mode
DARK_MODE_OLIVE = "#A3E635"  # Brighter Olive for dark mode
DARK_MODE_BG = "#111827"  # Dark background
DARK_MODE_CARD_BG = "#1F2937"  # Slightly lighter than background
DARK_MODE_TEXT = "#F9FAFB"  # Light text for dark mode
DARK_MODE_BORDER = "#374151"  # Border color for dark mode
DARK_MODE_INPUT_BG = "#1F2937"  # Input background for dark mode

# Current active mode (default to light)
DARK_BG = DARK_MODE_BG
CURRENT_BG = LIGHT_BG
CURRENT_TEXT = LIGHT_TEXT

# Keep old colors for backward compatibility
DARK_BLUE = DARK_PRIMARY
MEDIUM_BLUE = PRIMARY
LIGHT_BLUE = LIGHT_PRIMARY

# Shadows
SHADOW = "0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08)"
SHADOW_LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
DARK_SHADOW = "0 4px 6px rgba(0, 0, 0, 0.3), 0 1px 3px rgba(0, 0, 0, 0.2)"

# Light Mode Style Definitions
LIGHT_WINDOW_STYLE = f"""
    QWidget {{
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 14px;
        color: {LIGHT_TEXT};
        background-color: {LIGHT_BG};
    }}
    
    QLineEdit, QComboBox, QTextEdit {{
        padding: 12px;
        border: 1px solid {DARK_GRAY};
        border-radius: 8px;
        background-color: {WHITE};
    }}
    
    QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{
        border: 2px solid {PRIMARY};
    }}
    
    QPushButton {{
        background-color: {PRIMARY};
        color: {WHITE};
        border: none;
        border-radius: 8px;
        padding: 12px 20px;
        font-weight: bold;
        font-size: 14px;
    }}
    
    QPushButton:hover {{
        background-color: {DARK_PRIMARY};
    }}
    
    QPushButton:pressed {{
        background-color: {DARK_PRIMARY};
        padding-top: 14px;
        padding-bottom: 10px;
    }}
    
    QPushButton:disabled {{
        background-color: {DARK_GRAY};
    }}
    
    QLabel {{
        color: {LIGHT_TEXT};
    }}
    
    QProgressBar {{
        border: none;
        border-radius: 10px;
        background-color: {LIGHT_PRIMARY};
        text-align: center;
        color: {LIGHT_TEXT};
        font-weight: bold;
    }}
    
    QProgressBar::chunk {{
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {PRIMARY}, stop:1 {SECONDARY});
        border-radius: 10px;
    }}
"""

# Dark Mode Style Definitions
DARK_WINDOW_STYLE = f"""
    QWidget {{
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 14px;
        color: {DARK_MODE_TEXT};
        background-color: {DARK_MODE_BG};
    }}
    
    QLineEdit, QComboBox, QTextEdit {{
        padding: 12px;
        border: 1px solid {DARK_MODE_BORDER};
        border-radius: 8px;
        background-color: {DARK_MODE_INPUT_BG};
        color: {DARK_MODE_TEXT};
    }}
    
    QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{
        border: 2px solid {DARK_MODE_PRIMARY};
    }}
    
    QPushButton {{
        background-color: {DARK_MODE_PRIMARY};
        color: {DARK_MODE_TEXT};
        border: none;
        border-radius: 8px;
        padding: 12px 20px;
        font-weight: bold;
        font-size: 14px;
    }}
    
    QPushButton:hover {{
        background-color: {PRIMARY};
    }}
    
    QPushButton:pressed {{
        background-color: {PRIMARY};
        padding-top: 14px;
        padding-bottom: 10px;
    }}
    
    QPushButton:disabled {{
        background-color: {DARK_MODE_BORDER};
    }}
    
    QLabel {{
        color: {DARK_MODE_TEXT};
    }}
    
    QProgressBar {{
        border: none;
        border-radius: 10px;
        background-color: {DARK_MODE_CARD_BG};
        text-align: center;
        color: {DARK_MODE_TEXT};
        font-weight: bold;
    }}
    
    QProgressBar::chunk {{
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DARK_MODE_PRIMARY}, stop:1 {DARK_MODE_SECONDARY});
        border-radius: 10px;
    }}
"""

# Current active window style (default to light)
WINDOW_STYLE = LIGHT_WINDOW_STYLE

# Light Mode Component Styles
LIGHT_TITLE_STYLE = f"""
    font-size: 32px;
    font-weight: bold;
    color: {PRIMARY};
    margin-bottom: 20px;
"""

LIGHT_SUBTITLE_STYLE = f"""
    font-size: 20px;
    font-weight: bold;
    color: {DARK_PRIMARY};
    margin-bottom: 10px;
"""

LIGHT_TEXT_STYLE = f"""
    font-size: 16px;
    color: {LIGHT_TEXT};
"""

LIGHT_CARD_STYLE = f"""
    background-color: {WHITE};
    border-radius: 12px;
    padding: 20px;
    margin: 10px 0;
    border: 1px solid {LIGHT_PRIMARY};
    box-shadow: {SHADOW};
"""

LIGHT_GRADIENT_BUTTON = f"""
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {PRIMARY}, stop:1 {SECONDARY});
        color: {WHITE};
        border: none;
        border-radius: 8px;
        padding: 12px 20px;
        font-weight: bold;
        font-size: 14px;
    }}
    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {SECONDARY}, stop:1 {TERTIARY});
    }}
    QPushButton:pressed {{
        padding-top: 14px;
        padding-bottom: 10px;
    }}
"""

# Dark Mode Component Styles
DARK_TITLE_STYLE = f"""
    font-size: 32px;
    font-weight: bold;
    color: {DARK_MODE_PRIMARY};
    margin-bottom: 20px;
"""

DARK_SUBTITLE_STYLE = f"""
    font-size: 20px;
    font-weight: bold;
    color: {DARK_MODE_SECONDARY};
    margin-bottom: 10px;
"""

DARK_TEXT_STYLE = f"""
    font-size: 16px;
    color: {DARK_MODE_TEXT};
"""

DARK_CARD_STYLE = f"""
    background-color: {DARK_MODE_CARD_BG};
    border-radius: 12px;
    padding: 20px;
    margin: 10px 0;
    border: 1px solid {DARK_MODE_BORDER};
    box-shadow: {DARK_SHADOW};
"""

DARK_GRADIENT_BUTTON = f"""
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DARK_MODE_PRIMARY}, stop:1 {DARK_MODE_SECONDARY});
        color: {DARK_MODE_TEXT};
        border: none;
        border-radius: 8px;
        padding: 12px 20px;
        font-weight: bold;
        font-size: 14px;
    }}
    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DARK_MODE_SECONDARY}, stop:1 {DARK_MODE_TERTIARY});
    }}
    QPushButton:pressed {{
        padding-top: 14px;
        padding-bottom: 10px;
    }}
"""

# Current active component styles (default to light)
TITLE_STYLE = LIGHT_TITLE_STYLE
SUBTITLE_STYLE = LIGHT_SUBTITLE_STYLE
TEXT_STYLE = LIGHT_TEXT_STYLE
CARD_STYLE = LIGHT_CARD_STYLE
GRADIENT_BUTTON = LIGHT_GRADIENT_BUTTON

# Function to toggle between light and dark mode
def toggle_dark_mode(is_dark_mode):
    global WINDOW_STYLE, TITLE_STYLE, SUBTITLE_STYLE, TEXT_STYLE, CARD_STYLE, GRADIENT_BUTTON
    global CURRENT_BG, CURRENT_TEXT
    
    if is_dark_mode:
        WINDOW_STYLE = DARK_WINDOW_STYLE
        TITLE_STYLE = DARK_TITLE_STYLE
        SUBTITLE_STYLE = DARK_SUBTITLE_STYLE
        TEXT_STYLE = DARK_TEXT_STYLE
        CARD_STYLE = DARK_CARD_STYLE
        GRADIENT_BUTTON = DARK_GRADIENT_BUTTON
        CURRENT_BG = DARK_MODE_BG
        CURRENT_TEXT = DARK_MODE_TEXT
    else:
        WINDOW_STYLE = LIGHT_WINDOW_STYLE
        TITLE_STYLE = LIGHT_TITLE_STYLE
        SUBTITLE_STYLE = LIGHT_SUBTITLE_STYLE
        TEXT_STYLE = LIGHT_TEXT_STYLE
        CARD_STYLE = LIGHT_CARD_STYLE
        GRADIENT_BUTTON = LIGHT_GRADIENT_BUTTON
        CURRENT_BG = LIGHT_BG
        CURRENT_TEXT = LIGHT_TEXT
    
    return WINDOW_STYLE
