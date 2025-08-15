"""
Modern theme and styling configuration for FKDM.
Provides consistent, contemporary UI styling across the application.
"""

# Color palette for modern theme
COLORS = {
    'primary': '#4a90e2',
    'primary_dark': '#357abd',
    'primary_light': '#63a4ff',
    'secondary': '#50c878',
    'danger': '#e74c3c',
    'warning': '#f39c12',
    'success': '#27ae60',
    'background': '#f8f9fa',
    'surface': '#ffffff',
    'text': '#333333',
    'text_secondary': '#666666',
    'border': '#e0e0e0',
    'shadow': 'rgba(0, 0, 0, 0.1)'
}

# Main window styling
main_window_style = """
    QMainWindow {
        background-color: #f8f9fa;
    }
"""

# Modern scrollbar styling
scrollbar_style = """
    QScrollBar:vertical {
        background: #f0f0f0;
        width: 12px;
        border-radius: 6px;
    }
    QScrollBar::handle:vertical {
        background: #c0c0c0;
        border-radius: 6px;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:hover {
        background: #a0a0a0;
    }
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {
        height: 0px;
    }
"""

# Status bar styling
status_bar_style = """
    QStatusBar {
        background-color: #ffffff;
        border-top: 1px solid #e0e0e0;
        color: #666666;
        font-size: 13px;
        padding: 4px;
    }
"""

# Menu bar styling
menu_bar_style = """
    QMenuBar {
        background-color: #ffffff;
        border-bottom: 1px solid #e0e0e0;
        padding: 4px;
    }
    QMenuBar::item {
        padding: 8px 12px;
        background: transparent;
        border-radius: 4px;
    }
    QMenuBar::item:selected {
        background-color: #f0f0f0;
    }
    QMenuBar::item:pressed {
        background-color: #e0e0e0;
    }
    
    QMenu {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 4px;
    }
    QMenu::item {
        padding: 8px 24px;
        border-radius: 4px;
    }
    QMenu::item:selected {
        background-color: #f0f0f0;
        color: #4a90e2;
    }
"""

# Tooltip styling
tooltip_style = """
    QToolTip {
        background-color: #333333;
        color: white;
        border: none;
        padding: 8px;
        border-radius: 4px;
        font-size: 13px;
    }
"""

# Dialog styling
dialog_style = """
    QDialog {
        background-color: #ffffff;
    }
    QDialogButtonBox QPushButton {
        min-width: 80px;
        padding: 8px 16px;
    }
"""

# Tab widget styling
tab_widget_style = """
    QTabWidget::pane {
        border: 1px solid #e0e0e0;
        background-color: #ffffff;
        border-radius: 8px;
    }
    QTabBar::tab {
        background-color: #f0f0f0;
        padding: 10px 16px;
        margin-right: 4px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    QTabBar::tab:selected {
        background-color: #ffffff;
        border-bottom: 2px solid #4a90e2;
    }
    QTabBar::tab:hover {
        background-color: #e8e8e8;
    }
"""

# Combined global styles
global_modern_styles = f"""
    {main_window_style}
    {scrollbar_style}
    {status_bar_style}
    {menu_bar_style}
    {tooltip_style}
    {dialog_style}
    {tab_widget_style}
    
    * {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }}
    
    QWidget {{
        background-color: transparent;
    }}
    
    QLabel {{
        color: #333333;
        font-size: 14px;
    }}
    
    QGroupBox {{
        font-weight: 600;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        margin-top: 8px;
        padding-top: 8px;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
        background-color: #ffffff;
        color: #4a90e2;
    }}
"""