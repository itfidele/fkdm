"""
Desktop-native styling for FKDM.
Provides clean, native-looking styles that fit with OS conventions.
"""

# Color palette for desktop theme
DESKTOP_COLORS = {
    'background': '#f6f6f6',
    'surface': '#ffffff', 
    'border': '#d0d0d0',
    'text': '#333333',
    'text_secondary': '#666666',
    'accent': '#0078d4',
    'accent_hover': '#106ebe',
    'button_bg': '#e1e1e1',
    'button_hover': '#d2d2d2',
    'progress': '#0078d4'
}

# Main application styling
desktop_app_style = f"""
    QMainWindow {{
        background-color: {DESKTOP_COLORS['background']};
    }}
    
    QWidget {{
        font-family: -apple-system, "Segoe UI", "Ubuntu", system-ui, sans-serif;
        font-size: 13px;
    }}
    
    QLabel {{
        color: {DESKTOP_COLORS['text']};
        background-color: transparent;
    }}
    
    /* Group boxes */
    QGroupBox {{
        font-weight: 600;
        border: 1px solid {DESKTOP_COLORS['border']};
        border-radius: 4px;
        margin-top: 8px;
        padding-top: 8px;
        background-color: {DESKTOP_COLORS['surface']};
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
        background-color: {DESKTOP_COLORS['surface']};
        color: {DESKTOP_COLORS['text']};
    }}
    
    /* Line edits */
    QLineEdit {{
        padding: 6px 8px;
        border: 1px solid {DESKTOP_COLORS['border']};
        border-radius: 3px;
        background-color: {DESKTOP_COLORS['surface']};
        selection-background-color: {DESKTOP_COLORS['accent']};
    }}
    
    QLineEdit:focus {{
        border-color: {DESKTOP_COLORS['accent']};
        outline: none;
    }}
    
    QLineEdit[readOnly="true"] {{
        background-color: {DESKTOP_COLORS['background']};
        color: {DESKTOP_COLORS['text_secondary']};
    }}
    
    /* Buttons */
    QPushButton {{
        padding: 6px 16px;
        border: 1px solid {DESKTOP_COLORS['border']};
        border-radius: 3px;
        background-color: {DESKTOP_COLORS['button_bg']};
        color: {DESKTOP_COLORS['text']};
        font-weight: normal;
    }}
    
    QPushButton:hover {{
        background-color: {DESKTOP_COLORS['button_hover']};
        border-color: {DESKTOP_COLORS['accent']};
    }}
    
    QPushButton:pressed {{
        background-color: {DESKTOP_COLORS['border']};
    }}
    
    QPushButton:disabled {{
        background-color: #f0f0f0;
        color: #999999;
        border-color: #e0e0e0;
    }}
    
    /* Primary button style */
    QPushButton#primaryButton {{
        background-color: {DESKTOP_COLORS['accent']};
        color: white;
        border-color: {DESKTOP_COLORS['accent']};
        font-weight: 600;
    }}
    
    QPushButton#primaryButton:hover {{
        background-color: {DESKTOP_COLORS['accent_hover']};
        border-color: {DESKTOP_COLORS['accent_hover']};
    }}
    
    QPushButton#primaryButton:pressed {{
        background-color: #0c5394;
    }}
    
    QPushButton#primaryButton:disabled {{
        background-color: #cccccc;
        border-color: #cccccc;
    }}
    
    /* Progress bar */
    QProgressBar {{
        border: 1px solid {DESKTOP_COLORS['border']};
        border-radius: 3px;
        text-align: center;
        background-color: {DESKTOP_COLORS['surface']};
        color: {DESKTOP_COLORS['text']};
    }}
    
    QProgressBar::chunk {{
        background-color: {DESKTOP_COLORS['progress']};
        border-radius: 2px;
    }}
    
    /* Combo box */
    QComboBox {{
        padding: 6px 8px;
        border: 1px solid {DESKTOP_COLORS['border']};
        border-radius: 3px;
        background-color: {DESKTOP_COLORS['surface']};
    }}
    
    QComboBox:hover {{
        border-color: {DESKTOP_COLORS['accent']};
    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 4px solid {DESKTOP_COLORS['text_secondary']};
        margin-right: 4px;
    }}
    
    QComboBox QAbstractItemView {{
        border: 1px solid {DESKTOP_COLORS['border']};
        background-color: {DESKTOP_COLORS['surface']};
        selection-background-color: {DESKTOP_COLORS['accent']};
        selection-color: white;
    }}
    
    /* Status bar */
    QStatusBar {{
        background-color: {DESKTOP_COLORS['surface']};
        border-top: 1px solid {DESKTOP_COLORS['border']};
        color: {DESKTOP_COLORS['text_secondary']};
    }}
    
    /* Menu bar */
    QMenuBar {{
        background-color: {DESKTOP_COLORS['surface']};
        border-bottom: 1px solid {DESKTOP_COLORS['border']};
    }}
    
    QMenuBar::item {{
        padding: 4px 8px;
        background: transparent;
    }}
    
    QMenuBar::item:selected {{
        background-color: {DESKTOP_COLORS['button_hover']};
    }}
    
    QMenu {{
        background-color: {DESKTOP_COLORS['surface']};
        border: 1px solid {DESKTOP_COLORS['border']};
    }}
    
    QMenu::item {{
        padding: 4px 16px;
    }}
    
    QMenu::item:selected {{
        background-color: {DESKTOP_COLORS['accent']};
        color: white;
    }}
    
    /* Frames */
    QFrame {{
        background-color: {DESKTOP_COLORS['surface']};
        border: 1px solid {DESKTOP_COLORS['border']};
        border-radius: 4px;
    }}
"""