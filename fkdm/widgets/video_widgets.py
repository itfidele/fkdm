"""
Video-related widgets for YouTube download functionality.
Provides thumbnail preview, quality selection, and video information display.
"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QComboBox, QGroupBox, QSizePolicy, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QSize
from PyQt5.QtGui import QPixmap, QImage, QPalette
import requests
from io import BytesIO


class ThumbnailWidget(QFrame):
    """
    Widget for displaying video thumbnail with metadata overlay.
    """
    
    def __init__(self, parent=None):
        """
        Initialize thumbnail widget with placeholder.
        """
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """
        Create the thumbnail display layout.
        """
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet("""
            ThumbnailWidget {
                background-color: #f0f0f0;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        
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
                background-color: #000000;
                border-radius: 4px;
            }
        """)
        
        # Default placeholder text
        self.set_placeholder()
        
        layout.addWidget(self.image_label)
    
    def set_placeholder(self):
        """
        Display placeholder text when no thumbnail is available.
        """
        self.image_label.setText("Video thumbnail will appear here")
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 2px dashed #dee2e6;
                border-radius: 4px;
                color: #6c757d;
                font-size: 14px;
                padding: 40px;
            }
        """)
    
    def set_loading(self):
        """
        Display loading indicator.
        """
        self.image_label.setText("Loading thumbnail...")
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                color: #999999;
                font-size: 14px;
                padding: 40px;
                font-style: italic;
            }
        """)
    
    def set_thumbnail(self, image_data: bytes, duration: str = None):
        """
        Set thumbnail image from bytes data.
        
        Args:
            image_data: Image data in bytes
            duration: Video duration string to display
        """
        try:
            # Create QImage from bytes
            qimage = QImage()
            qimage.loadFromData(image_data)
            
            if not qimage.isNull():
                # Scale image to fit
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
        """
        Load and set thumbnail from URL with loading indicator.
        
        Args:
            url: Thumbnail image URL
            duration: Video duration string to display
        """
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
        """
        Clear the thumbnail and reset to placeholder.
        """
        self.set_placeholder()


class VideoInfoWidget(QGroupBox):
    """
    Widget for displaying video information and metadata.
    """
    
    def __init__(self, parent=None):
        """
        Initialize video info widget.
        """
        super().__init__("Video Information", parent)
        self.setup_ui()
    
    def setup_ui(self):
        """
        Create the video information display layout.
        """
        self.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: #ffffff;
                color: #4a90e2;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Title
        self.title_label = QLabel("No video loaded")
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                padding: 4px 0;
            }
        """)
        
        # Uploader
        self.uploader_label = QLabel("")
        self.uploader_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #666666;
                padding: 2px 0;
            }
        """)
        
        # Stats row
        stats_layout = QHBoxLayout()
        
        self.duration_label = QLabel("")
        self.duration_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666666;
            }
        """)
        
        self.views_label = QLabel("")
        self.views_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666666;
            }
        """)
        
        self.size_label = QLabel("")
        self.size_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666666;
            }
        """)
        
        stats_layout.addWidget(self.duration_label)
        stats_layout.addWidget(QLabel(" | "))
        stats_layout.addWidget(self.views_label)
        stats_layout.addWidget(QLabel(" | "))
        stats_layout.addWidget(self.size_label)
        stats_layout.addStretch()
        
        # Add all to main layout
        layout.addWidget(self.title_label)
        layout.addWidget(self.uploader_label)
        layout.addLayout(stats_layout)
    
    def update_info(self, video_info):
        """
        Update display with video information.
        
        Args:
            video_info: YouTubeInfo object containing video metadata
        """
        if video_info:
            self.title_label.setText(video_info.title)
            self.uploader_label.setText(f"By {video_info.uploader}")
            self.duration_label.setText(f"Duration: {video_info.get_duration_string()}")
            
            # Format view count
            views = video_info.view_count
            if views >= 1000000:
                views_str = f"{views/1000000:.1f}M views"
            elif views >= 1000:
                views_str = f"{views/1000:.1f}K views"
            else:
                views_str = f"{views} views"
            self.views_label.setText(views_str)
            
            # File size (if available)
            if video_info.filesize:
                size_mb = video_info.filesize / (1024 * 1024)
                self.size_label.setText(f"Size: ~{size_mb:.1f} MB")
            else:
                self.size_label.setText("Size: Calculating...")
        else:
            self.clear()
    
    def clear(self):
        """
        Clear all video information.
        """
        self.title_label.setText("No video loaded")
        self.uploader_label.setText("")
        self.duration_label.setText("")
        self.views_label.setText("")
        self.size_label.setText("")


class QualitySelectionWidget(QGroupBox):
    """
    Widget for selecting video download quality.
    """
    
    quality_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """
        Initialize quality selection widget.
        """
        super().__init__("Download Quality", parent)
        self.setup_ui()
    
    def setup_ui(self):
        """
        Create the quality selection layout.
        """
        self.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: #ffffff;
                color: #4a90e2;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Quality combo box
        self.quality_combo = QComboBox()
        self.quality_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                font-size: 14px;
            }
            QComboBox:hover {
                border-color: #4a90e2;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666666;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #e0e0e0;
                background-color: white;
                selection-background-color: #4a90e2;
            }
        """)
        
        # Default options
        self.quality_combo.addItem("Select quality after loading video")
        self.quality_combo.setEnabled(False)
        self.quality_combo.currentTextChanged.connect(self.on_quality_changed)
        
        layout.addWidget(self.quality_combo)
    
    def set_qualities(self, qualities: list):
        """
        Update available quality options.
        
        Args:
            qualities: List of tuples (format_id, description)
        """
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
        """
        Handle quality selection change.
        
        Args:
            text: Selected quality description
        """
        if self.quality_combo.isEnabled() and self.quality_combo.currentData():
            self.quality_changed.emit(self.quality_combo.currentData())
    
    def get_selected_format(self) -> str:
        """
        Get the currently selected format ID.
        
        Returns:
            Format ID string or 'best' if none selected
        """
        if self.quality_combo.isEnabled() and self.quality_combo.currentData():
            return self.quality_combo.currentData()
        return 'best'
    
    def clear(self):
        """
        Reset quality selection to default state.
        """
        self.quality_combo.clear()
        self.quality_combo.addItem("Select quality after loading video")
        self.quality_combo.setEnabled(False)