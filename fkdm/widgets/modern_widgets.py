"""
Modern custom widgets for FKDM download manager.
Provides reusable, styled components for a modern UI experience.
"""

from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLineEdit, QLabel, 
    QVBoxLayout, QHBoxLayout, QProgressBar,
    QFrame, QGraphicsDropShadowEffect, QToolButton
)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QPalette, QColor, QFont, QIcon
from qtawesome import icon as qta_icon


class ModernCard(QFrame):
    """
    A modern card widget with shadow effects and rounded corners.
    Used as a container for grouped UI elements.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the card appearance with modern styling."""
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet("""
            ModernCard {
                background-color: #ffffff;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
                padding: 20px;
            }
        """)
        
        # Add shadow effect for depth
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)


class ModernLineEdit(QLineEdit):
    """
    Enhanced line edit with modern styling and animations.
    Features focus animations and icon support.
    """
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setup_ui()
    
    def setup_ui(self):
        """Apply modern styling to the line edit."""
        self.setStyleSheet("""
            ModernLineEdit {
                padding: 12px 16px;
                font-size: 14px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: #f8f9fa;
                color: #333333;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }
            ModernLineEdit:focus {
                border-color: #4a90e2;
                background-color: #ffffff;
                outline: none;
            }
            ModernLineEdit:hover {
                border-color: #b0b0b0;
            }
            ModernLineEdit[readOnly="true"] {
                background-color: #f0f0f0;
                color: #666666;
            }
        """)


class ModernButton(QPushButton):
    """
    Modern styled button with hover effects and animations.
    Supports primary and secondary button styles.
    """
    
    def __init__(self, text="", button_type="primary", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self.setup_ui()
    
    def setup_ui(self):
        """Apply modern button styling based on button type."""
        base_style = """
            ModernButton {
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                border-radius: 8px;
                border: none;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                text-transform: none;
                cursor: pointer;
            }
        """
        
        if self.button_type == "primary":
            self.setStyleSheet(base_style + """
                ModernButton {
                    background-color: #4a90e2;
                    color: white;
                }
                ModernButton:hover {
                    background-color: #357abd;
                }
                ModernButton:pressed {
                    background-color: #2968a3;
                }
                ModernButton:disabled {
                    background-color: #cccccc;
                    color: #666666;
                }
            """)
        else:  # secondary
            self.setStyleSheet(base_style + """
                ModernButton {
                    background-color: #ffffff;
                    color: #4a90e2;
                    border: 2px solid #4a90e2;
                }
                ModernButton:hover {
                    background-color: #f0f7ff;
                    border-color: #357abd;
                }
                ModernButton:pressed {
                    background-color: #e1f0ff;
                }
                ModernButton:disabled {
                    background-color: #f5f5f5;
                    color: #999999;
                    border-color: #cccccc;
                }
            """)
        
        # Set cursor
        self.setCursor(Qt.PointingHandCursor)


class ModernProgressBar(QProgressBar):
    """
    Enhanced progress bar with smooth animations and modern styling.
    Shows download progress with percentage and optional status text.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Apply modern progress bar styling."""
        self.setTextVisible(True)
        self.setStyleSheet("""
            ModernProgressBar {
                border: none;
                border-radius: 8px;
                background-color: #e9ecef;
                text-align: center;
                font-size: 12px;
                font-weight: 600;
                color: #495057;
                height: 24px;
            }
            ModernProgressBar::chunk {
                border-radius: 8px;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #4a90e2,
                    stop: 1 #63a4ff
                );
            }
        """)


class DownloadInfoWidget(QWidget):
    """
    Widget to display download information including speed, size, and time remaining.
    Updates dynamically during downloads.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Create the download info display layout."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)
        
        # Speed indicator
        self.speed_label = QLabel("Speed: --")
        self.speed_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 13px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }
        """)
        
        # Size indicator
        self.size_label = QLabel("Size: --")
        self.size_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 13px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }
        """)
        
        # Time remaining
        self.time_label = QLabel("Time: --")
        self.time_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 13px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }
        """)
        
        layout.addWidget(self.speed_label)
        layout.addWidget(QLabel(" | "))
        layout.addWidget(self.size_label)
        layout.addWidget(QLabel(" | "))
        layout.addWidget(self.time_label)
        layout.addStretch()
    
    def update_info(self, speed=None, size=None, time_remaining=None):
        """
        Update download information display.
        
        Args:
            speed: Download speed in bytes/second
            size: Total size in bytes
            time_remaining: Estimated time remaining in seconds
        """
        if speed is not None:
            speed_mb = speed / (1024 * 1024)
            self.speed_label.setText(f"Speed: {speed_mb:.2f} MB/s")
        
        if size is not None:
            size_mb = size / (1024 * 1024)
            self.size_label.setText(f"Size: {size_mb:.2f} MB")
        
        if time_remaining is not None:
            mins = int(time_remaining // 60)
            secs = int(time_remaining % 60)
            self.time_label.setText(f"Time: {mins:02d}:{secs:02d}")


class URLInputWidget(QWidget):
    """
    Custom widget for URL input with validation and paste button.
    Provides visual feedback for valid/invalid URLs.
    """
    
    url_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Create the URL input widget layout."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # URL input field
        self.url_input = ModernLineEdit("Enter download URL...")
        self.url_input.textChanged.connect(self.validate_url)
        
        # Paste button
        self.paste_button = QToolButton()
        self.paste_button.setIcon(qta_icon('fa5s.clipboard', color='#4a90e2'))
        self.paste_button.setToolTip("Paste from clipboard")
        self.paste_button.clicked.connect(self.paste_from_clipboard)
        self.paste_button.setStyleSheet("""
            QToolButton {
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QToolButton:hover {
                background-color: #f0f0f0;
            }
        """)
        
        layout.addWidget(self.url_input)
        layout.addWidget(self.paste_button)
    
    def validate_url(self, url):
        """
        Validate the entered URL and provide visual feedback.
        
        Args:
            url: The URL string to validate
        """
        if url.startswith(('http://', 'https://', 'ftp://')):
            self.url_input.setStyleSheet(self.url_input.styleSheet().replace('#e0e0e0', '#4caf50'))
            self.url_changed.emit(url)
        elif url:
            self.url_input.setStyleSheet(self.url_input.styleSheet().replace('#4caf50', '#e0e0e0'))
    
    def paste_from_clipboard(self):
        """Paste URL from system clipboard."""
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        self.url_input.setText(clipboard.text())
    
    def get_url(self):
        """Get the current URL text."""
        return self.url_input.text()
    
    def clear(self):
        """Clear the URL input."""
        self.url_input.clear()