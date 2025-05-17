# This palette and style system is inspired by tailwind.config.ts (see root of project)
# All color values and design decisions are mapped from the Tailwind 'teamtrack' theme.
# If you update the Tailwind config, please mirror changes here for design consistency.

# Tailwind-inspired teamtrack color palette
PRIMARY = "#1E40AF"      # Deep blue
SECONDARY = "#0D9488"    # Teal
ACCENT = "#F59E0B"       # Amber
LIGHT = "#F8FAFC"        # Light background
DARK = "#1E293B"         # Dark text/background
SUCCESS = "#10B981"      # Green
ERROR = "#EF4444"        # Red
WARNING = "#F59E0B"      # Amber
INFO = "#3B82F6"         # Blue

# Additional Tailwind-inspired olive colors for legacy/compatibility
OLIVE = "#65A30D"        # Olive green (Tailwind: lime-600)
LIGHT_OLIVE = "#D9F99D"  # Light olive (Tailwind: lime-100)
CREAM = "#FEFCE8"        # Cream (Tailwind: yellow-50)
PEACH = "#FDBA74"        # Peach (Tailwind: orange-300)

# Utility
BORDER_RADIUS = "14px"
SHADOW = "0 4px 24px 0 rgba(30,64,175,0.08)"

# Common styles
WINDOW_STYLE = f"""
    QWidget {{
        background: {LIGHT};
    }}
    QLabel {{
        color: {DARK};
        font-family: 'Segoe UI', 'Inter', 'Arial', sans-serif;
    }}
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {PRIMARY}, stop:1 {ACCENT});
        color: white;
        border: none;
        border-radius: {BORDER_RADIUS};
        padding: 10px 22px;
        font-weight: 600;
        font-size: 16px;
        letter-spacing: 0.5px;
        box-shadow: {SHADOW};
        transition: background 0.2s, transform 0.12s;
    }}
    QPushButton:hover {{
        background: {SECONDARY};
        color: white;
        transform: scale(1.03);
    }}
    QPushButton:pressed {{
        background: {PRIMARY};
        color: {ACCENT};
        transform: scale(0.97);
    }}
    QLineEdit, QComboBox {{
        background: white;
        border: 2px solid {PRIMARY};
        border-radius: {BORDER_RADIUS};
        padding: 10px 14px;
        color: {DARK};
        font-size: 16px;
        font-family: 'Segoe UI', 'Inter', 'Arial', sans-serif;
        transition: border 0.2s;
    }}
    QLineEdit:focus, QComboBox:focus {{
        border: 2px solid {ACCENT};
        outline: none;
    }}
    QFrame {{
        background: {LIGHT};
        border-radius: {BORDER_RADIUS};
        box-shadow: {SHADOW};
        border: 1px solid {PRIMARY};
    }}
    QScrollArea {{
        border: none;
        background: transparent;
    }}
"""

TITLE_STYLE = f"""
    font-size: 32px;
    font-weight: 800;
    color: {PRIMARY};
    letter-spacing: 1px;
    font-family: 'Segoe UI', 'Inter', 'Arial', sans-serif;
    margin: 20px 0 10px 0;
    text-shadow: 0 2px 8px rgba(30,64,175,0.08);
"""

SUBTITLE_STYLE = f"""
    font-size: 22px;
    font-weight: 600;
    color: {SECONDARY};
    font-family: 'Segoe UI', 'Inter', 'Arial', sans-serif;
    margin-bottom: 10px;
"""

TEXT_STYLE = f"""
    font-size: 16px;
    color: {DARK};
    font-family: 'Segoe UI', 'Inter', 'Arial', sans-serif;
"""

SUCCESS_STYLE = f"color: {SUCCESS}; font-weight: 600;"
ERROR_STYLE = f"color: {ERROR}; font-weight: 600;"
INFO_STYLE = f"color: {INFO}; font-weight: 600;"
ACCENT_STYLE = f"color: {ACCENT}; font-weight: 600;"

CARD_STYLE = f"""
    background: white;
    border-radius: {BORDER_RADIUS};
    box-shadow: {SHADOW};
    border: 1px solid {PRIMARY};
    padding: 18px 22px;
"""
