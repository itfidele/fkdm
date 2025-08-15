"""
Desktop-native widgets for FKDM download manager.
Simple, clean widgets that follow desktop UI conventions.
"""

from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLineEdit, QLabel, 
    QVBoxLayout, QHBoxLayout, QProgressBar,
    QFrame, QGroupBox, QComboBox, QToolButton,
    QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class SimpleLineEdit(QLineEdit):
    """
    Simple line edit with desktop-native styling.
    """
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        if placeholder:
            self.setPlaceholderText(placeholder)


class SimpleButton(QPushButton):
    """
    Simple button with desktop-native styling.
    """
    
    def __init__(self, text="", is_primary=False, parent=None):
        super().__init__(text, parent)
        if is_primary:
            self.setObjectName("primaryButton")


class SimpleProgressBar(QProgressBar):
    """
    Simple progress bar with desktop-native styling.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(True)


class URLInputWidget(QWidget):
    """
    Simple URL input widget with paste functionality.
    """
    
    url_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Create the URL input layout."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        
        # URL input field
        self.url_input = SimpleLineEdit("Enter download URL...")
        self.url_input.textChanged.connect(self.validate_url)
        
        # Paste button (simplified, no icon)
        self.paste_button = QPushButton("Paste")
        self.paste_button.setMaximumWidth(60)
        self.paste_button.setToolTip("Paste from clipboard")
        self.paste_button.clicked.connect(self.paste_from_clipboard)
        
        layout.addWidget(self.url_input)
        layout.addWidget(self.paste_button)
    
    def validate_url(self, url):
        """Validate URL and emit signal."""
        if url.startswith(('http://', 'https://', 'ftp://')):
            self.url_changed.emit(url)
    
    def paste_from_clipboard(self):
        """Paste URL from system clipboard."""
        clipboard = QApplication.clipboard()
        self.url_input.setText(clipboard.text())
    
    def get_url(self):
        """Get the current URL text."""
        return self.url_input.text()
    
    def clear(self):
        """Clear the URL input."""
        self.url_input.clear()


class ThumbnailWidget(QFrame):
    """
    Simple thumbnail display widget.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Create the thumbnail display layout."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Thumbnail image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(False)
        self.image_label.setMinimumSize(320, 180)
        self.image_label.setMaximumSize(480, 270)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
            }
        """)
        
        self.set_placeholder()
        layout.addWidget(self.image_label)
    
    def set_placeholder(self):
        """Display placeholder text."""
        self.image_label.setText("Video thumbnail will appear here")
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #f8f8f8;
                border: 1px dashed #d0d0d0;
                border-radius: 3px;
                color: #666666;
                padding: 40px;
            }
        """)
    
    def set_loading(self):
        """Display loading indicator."""
        self.image_label.setText("Loading thumbnail...")
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
                color: #999999;
                padding: 40px;
                font-style: italic;
            }
        """)
    
    def set_thumbnail(self, image_data: bytes, duration: str = None):
        """Set thumbnail image from bytes data."""
        try:
            from PyQt5.QtGui import QImage, QPixmap
            qimage = QImage()
            qimage.loadFromData(image_data)
            
            if not qimage.isNull():
                pixmap = QPixmap.fromImage(qimage)
                scaled_pixmap = pixmap.scaled(
                    self.image_label.maximumSize(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
                self.image_label.setStyleSheet("")
            else:
                self.set_placeholder()
        except Exception:
            self.set_placeholder()
    
    def set_thumbnail_from_url(self, url: str, duration: str = None):
        """Load and set thumbnail from URL with loading indicator."""
        # Show loading state immediately
        self.set_loading()
        
        # Create thumbnail loading thread
        from PyQt5.QtCore import QThread, pyqtSignal
        
        class ThumbnailLoader(QThread):
            thumbnail_loaded = pyqtSignal(bytes)
            thumbnail_failed = pyqtSignal()
            
            def __init__(self, url):
                super().__init__()
                self.url = url
            
            def run(self):
                try:
                    import requests
                    response = requests.get(self.url, timeout=10)
                    if response.status_code == 200:
                        self.thumbnail_loaded.emit(response.content)
                    else:
                        self.thumbnail_failed.emit()
                except Exception:
                    self.thumbnail_failed.emit()
        
        # Create and start loader
        self.thumbnail_loader = ThumbnailLoader(url)
        self.thumbnail_loader.thumbnail_loaded.connect(self.set_thumbnail)
        self.thumbnail_loader.thumbnail_failed.connect(self.set_placeholder)
        self.thumbnail_loader.start()
    
    def clear(self):
        """Clear the thumbnail."""
        self.set_placeholder()


class VideoInfoWidget(QGroupBox):
    """
    Simple video information display.
    """
    
    def __init__(self, parent=None):
        super().__init__("Video Information", parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Create the video info layout."""
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        
        # Title
        self.title_label = QLabel("No video loaded")
        self.title_label.setWordWrap(True)
        font = QFont()
        font.setBold(True)
        self.title_label.setFont(font)
        
        # Details
        self.details_label = QLabel("")
        self.details_label.setStyleSheet("color: #666666;")
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.details_label)
    
    def update_info(self, video_info):
        """Update display with video information."""
        if video_info:
            self.title_label.setText(video_info.title)
            
            details = f"By {video_info.uploader}"
            details += f" • {video_info.get_duration_string()}"
            
            # Format view count
            views = video_info.view_count
            if views >= 1000000:
                details += f" • {views/1000000:.1f}M views"
            elif views >= 1000:
                details += f" • {views/1000:.1f}K views"
            else:
                details += f" • {views} views"
            
            self.details_label.setText(details)
        else:
            self.clear()
    
    def clear(self):
        """Clear video information."""
        self.title_label.setText("No video loaded")
        self.details_label.setText("")


class QualitySelectionWidget(QGroupBox):
    """
    Simple quality selection widget.
    """
    
    quality_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__("Download Quality", parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Create the quality selection layout."""
        layout = QVBoxLayout(self)
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItem("Select quality after loading video")
        self.quality_combo.setEnabled(False)
        self.quality_combo.currentTextChanged.connect(self.on_quality_changed)
        
        layout.addWidget(self.quality_combo)
    
    def set_qualities(self, qualities: list):
        """Update available quality options."""
        self.quality_combo.clear()
        
        if qualities:
            for format_id, description in qualities:
                self.quality_combo.addItem(description, format_id)
            self.quality_combo.setEnabled(True)
            self.quality_combo.setCurrentIndex(0)
        else:
            self.quality_combo.addItem("No qualities available")
            self.quality_combo.setEnabled(False)
    
    def on_quality_changed(self, text):
        """Handle quality selection change."""
        if self.quality_combo.isEnabled() and self.quality_combo.currentData():
            self.quality_changed.emit(self.quality_combo.currentData())
    
    def get_selected_format(self) -> str:
        """Get the currently selected format ID."""
        if self.quality_combo.isEnabled() and self.quality_combo.currentData():
            return self.quality_combo.currentData()
        return 'best'
    
    def clear(self):
        """Reset quality selection."""
        self.quality_combo.clear()
        self.quality_combo.addItem("Select quality after loading video")
        self.quality_combo.setEnabled(False)


class DownloadInfoWidget(QWidget):
    """
    Simple download information display.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Create the download info layout."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        
        self.info_label = QLabel("Ready")
        self.info_label.setStyleSheet("color: #666666; font-size: 12px;")
        
        layout.addWidget(self.info_label)
        layout.addStretch()
    
    def update_info(self, speed=None, size=None, time_remaining=None):
        """Update download information display."""
        info_parts = []
        
        if speed is not None:
            speed_mb = speed / (1024 * 1024)
            info_parts.append(f"Speed: {speed_mb:.1f} MB/s")
        
        if size is not None:
            size_mb = size / (1024 * 1024)
            info_parts.append(f"Size: {size_mb:.1f} MB")
        
        if time_remaining is not None:
            mins = int(time_remaining // 60)
            secs = int(time_remaining % 60)
            info_parts.append(f"Time: {mins:02d}:{secs:02d}")
        
        if info_parts:
            self.info_label.setText(" • ".join(info_parts))
        else:
            self.info_label.setText("Ready")