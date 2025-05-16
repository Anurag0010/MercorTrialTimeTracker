# Color palette
OLIVE = "#69754F"
LIGHT_OLIVE = "#A9B86E"
CREAM = "#F6EFD6"
PEACH = "#F4C183"

# Common styles
WINDOW_STYLE = f"""
    QWidget {{
        background-color: {CREAM};
    }}
    QLabel {{
        color: {OLIVE};
    }}
    QPushButton {{
        background-color: {PEACH};
        color: {OLIVE};
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {LIGHT_OLIVE};
    }}
    QLineEdit {{
        background-color: white;
        border: 2px solid {LIGHT_OLIVE};
        border-radius: 6px;
        padding: 6px;
        color: {OLIVE};
    }}
    QComboBox {{
        background-color: white;
        border: 2px solid {LIGHT_OLIVE};
        border-radius: 6px;
        padding: 6px;
        color: {OLIVE};
    }}
    QFrame {{
        background-color: {LIGHT_OLIVE};
        border-radius: 12px;
    }}
"""

TITLE_STYLE = f"""
    font-size: 32px;
    font-weight: bold;
    color: {OLIVE};
    margin: 20px;
"""

SUBTITLE_STYLE = f"""
    font-size: 22px;
    font-weight: bold;
    color: {OLIVE};
"""

TEXT_STYLE = f"""
    font-size: 16px;
    color: {OLIVE};
"""
