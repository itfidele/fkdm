"""
FKDM Desktop Application - Clean, native desktop interface
Simple, efficient download manager with YouTube support
"""

import os
import sys
import time
from PyQt5.QtCore import QSettings, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout,
    QApplication, QMainWindow, QFileDialog, QProgressBar, 
    QStatusBar, QMenuBar, QMenu, QAction, QLabel, QGroupBox,
    QMessageBox
)
from PyQt5.QtGui import QIcon, QFont
from notifypy import Notify

from fkdm.config.desktop_styles import desktop_app_style
from fkdm.config import settings
from fkdm.widgets.desktop_widgets import (
    SimpleLineEdit, SimpleButton, SimpleProgressBar, 
    DownloadInfoWidget, URLInputWidget, ThumbnailWidget,
    VideoInfoWidget, QualitySelectionWidget
)
from fkdm.youtube.downloader import (
    YouTubeDownloadThread, get_video_info, is_youtube_url, YouTubeInfo
)

# Import the original DownloadThread from FKDM.py
import pycurl
import io
from notifypy import Notify

notification = Notify()

class DownloadThread(QThread):
    """Background thread for regular file downloads."""
    
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str)
    speed_signal = pyqtSignal(float)
    size_signal = pyqtSignal(float, float)

    def __init__(self, url, filename: str):
        super().__init__()
        self.url = url
        self.filename = filename
        self.total_bytes = None
        self.downloaded_bytes = 0
        self.start_time = None
        self.last_update_time = None
        self.last_downloaded_bytes = 0

    def run(self):
        self.status_signal.emit("Download started")
        self.start_time = time.time()
        self.last_update_time = self.start_time
        
        buffer = io.BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, self.url)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(pycurl.NOPROGRESS, 0)
        c.setopt(pycurl.PROGRESSFUNCTION, self.progress_function)
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.setopt(pycurl.MAXREDIRS, 5)
        
        fp = open(self.filename, "wb")
        c.setopt(pycurl.WRITEDATA, fp)

        try:
            c.perform()
        except pycurl.error as e:
            self.status_signal.emit(f'Error: {e}')
        finally:
            c.close()
            fp.close()

        notification.title = "Download Completed"
        notification.message = os.path.basename(self.filename)
        notification.send()
        
        self.status_signal.emit("Download Complete!")

    def progress_function(self, download_t, download_d, upload_t, upload_d):
        if download_t > 0:
            percent = int((download_d / download_t) * 100)
            self.progress_signal.emit(percent)
            
            current_time = time.time()
            time_diff = current_time - self.last_update_time
            
            if time_diff >= 0.5:
                bytes_diff = download_d - self.last_downloaded_bytes
                speed = bytes_diff / time_diff if time_diff > 0 else 0
                self.speed_signal.emit(speed)
                
                self.last_update_time = current_time
                self.last_downloaded_bytes = download_d
            
            self.size_signal.emit(download_d, download_t)


class FKDMApp(QMainWindow):
    """Main FKDM application window with desktop-native interface."""
    
    def __init__(self) -> None:
        super().__init__()
        self.settings = QSettings("FKDM", "FKDM")
        self.download_thread = None
        self.youtube_thread = None
        self.current_video_info = None
        self.initUI()
        self.setup_menu_bar()

    def initUI(self):
        """Initialize the user interface."""
        self.setWindowTitle("FKDM Download Manager")
        self.setGeometry(100, 100, 600, 450)
        self.setStyleSheet(desktop_app_style)
        
        # Store initial window size for restoration
        self.initial_size = self.size()
        self.compact_height = 300  # Smaller height when download completes
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # URL Input
        url_group = QGroupBox("Download URL")
        url_layout = QVBoxLayout(url_group)
        
        self.url_widget = URLInputWidget()
        self.url_widget.url_changed.connect(self.on_url_changed)
        url_layout.addWidget(self.url_widget)
        main_layout.addWidget(url_group)
        
        # Save Location
        location_group = QGroupBox("Save Location")
        location_layout = QVBoxLayout(location_group)
        
        location_input_layout = QHBoxLayout()
        self.save_directory_input = SimpleLineEdit("Choose save location...")
        self.save_directory_input.setReadOnly(True)
        saved_location = self.settings.value("save_location", "")
        if saved_location:
            self.save_directory_input.setText(saved_location)
        
        self.browse_button = SimpleButton("Browse")
        self.browse_button.clicked.connect(self.browse_location)
        
        location_input_layout.addWidget(self.save_directory_input)
        location_input_layout.addWidget(self.browse_button)
        location_layout.addLayout(location_input_layout)
        main_layout.addWidget(location_group)
        
        # Video Preview (hidden by default)
        self.video_preview_group = QGroupBox("Video Preview")
        video_preview_layout = QVBoxLayout(self.video_preview_group)
        
        preview_content_layout = QHBoxLayout()
        
        self.thumbnail_widget = ThumbnailWidget()
        preview_content_layout.addWidget(self.thumbnail_widget)
        
        info_layout = QVBoxLayout()
        self.video_info_widget = VideoInfoWidget()
        info_layout.addWidget(self.video_info_widget)
        
        self.quality_widget = QualitySelectionWidget()
        info_layout.addWidget(self.quality_widget)
        info_layout.addStretch()
        
        preview_content_layout.addLayout(info_layout)
        video_preview_layout.addLayout(preview_content_layout)
        
        self.video_preview_group.setVisible(False)
        main_layout.addWidget(self.video_preview_group)
        
        # Download Controls
        controls_group = QGroupBox("Download")
        controls_layout = QVBoxLayout(controls_group)
        
        self.download_button = SimpleButton("Start Download", is_primary=True)
        self.download_button.clicked.connect(self.download_file)
        controls_layout.addWidget(self.download_button)
        
        self.progress_bar = SimpleProgressBar()
        controls_layout.addWidget(self.progress_bar)
        
        self.download_info = DownloadInfoWidget()
        controls_layout.addWidget(self.download_info)
        
        main_layout.addWidget(controls_group)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def resize_window_compact(self):
        """Resize window to compact size when download completes."""
        current_size = self.size()
        self.resize(current_size.width(), self.compact_height)
    
    def resize_window_full(self):
        """Resize window back to full size when needed."""
        self.resize(self.initial_size)

    def setup_menu_bar(self):
        """Create application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        new_action = QAction('New Download', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(lambda: self.url_widget.url_input.setFocus())
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def on_url_changed(self, url: str):
        """Handle URL input changes."""
        if is_youtube_url(url):
            self.video_preview_group.setVisible(True)
            self.status_bar.showMessage("Loading video information...")
            
            # Resize window back to full size for YouTube videos
            self.resize_window_full()
            
            self.load_youtube_info(url)
        else:
            self.video_preview_group.setVisible(False)
            self.current_video_info = None
    
    def load_youtube_info(self, url: str):
        """Load YouTube video information in background."""
        class InfoThread(QThread):
            info_ready = pyqtSignal(object)
            error = pyqtSignal(str)
            
            def __init__(self, url):
                super().__init__()
                self.url = url
            
            def run(self):
                try:
                    info = get_video_info(self.url)
                    if info:
                        self.info_ready.emit(info)
                    else:
                        self.error.emit("Failed to load video information")
                except Exception as e:
                    self.error.emit(str(e))
        
        self.info_thread = InfoThread(url)
        self.info_thread.info_ready.connect(self.on_youtube_info_loaded)
        self.info_thread.error.connect(lambda err: self.status_bar.showMessage(f"Error: {err}"))
        self.info_thread.start()
    
    def on_youtube_info_loaded(self, video_info: YouTubeInfo):
        """Handle loaded YouTube video information."""
        self.current_video_info = video_info
        self.video_info_widget.update_info(video_info)
        
        if video_info.thumbnail:
            self.thumbnail_widget.set_thumbnail_from_url(video_info.thumbnail)
        
        qualities = video_info.get_available_qualities()
        self.quality_widget.set_qualities(qualities)
        
        self.status_bar.showMessage("Video information loaded")
    
    def browse_location(self):
        """Open file dialog to select download directory."""
        options = QFileDialog.Options()
        current_dir = self.save_directory_input.text() or os.path.expanduser("~")
        folder_path = QFileDialog.getExistingDirectory(
            self, "Select Download Location", current_dir, options=options
        )
        if folder_path:
            self.save_directory_input.setText(folder_path)
            self.settings.setValue("save_location", folder_path)
            self.settings.sync()
    
    def download_file(self):
        """Initiate file download."""
        url = self.url_widget.get_url().strip()
        save_location = self.save_directory_input.text().strip()
        
        # Validate inputs
        if not url:
            self.status_bar.showMessage("Please enter a URL")
            return
        
        if not url.startswith(('http://', 'https://', 'ftp://')):
            self.status_bar.showMessage("Please enter a valid URL")
            return
        
        if not save_location:
            self.status_bar.showMessage("Please select a download location")
            return
        
        if not os.path.exists(save_location):
            self.status_bar.showMessage("Selected directory does not exist")
            return
        
        # Save settings
        self.settings.setValue("save_location", save_location)
        self.settings.sync()
        
        # Check if YouTube video
        if is_youtube_url(url) and self.current_video_info:
            self.start_youtube_download(url, save_location)
        else:
            self.start_regular_download(url, save_location)
    
    def start_youtube_download(self, url: str, save_location: str):
        """Start YouTube download."""
        title = self.current_video_info.title
        # Clean filename
        for char in '<>:"|?*/\\':
            title = title.replace(char, '_')
        file_name = f"{title[:200]}.mp4"
        file_path = os.path.join(save_location, file_name)
        
        # Handle duplicate files
        counter = 1
        base_path = file_path
        while os.path.exists(file_path):
            name, ext = os.path.splitext(base_path)
            file_path = f"{name}_{counter}{ext}"
            counter += 1
        
        format_id = self.quality_widget.get_selected_format()
        
        self.progress_bar.setValue(0)
        self.download_button.setEnabled(False)
        self.download_button.setText("Downloading...")
        
        self.youtube_thread = YouTubeDownloadThread(url, file_path, format_id)
        self.youtube_thread.progress_signal.connect(self.update_progress)
        self.youtube_thread.status_signal.connect(self.update_status)
        self.youtube_thread.speed_signal.connect(self.update_speed)
        self.youtube_thread.error_signal.connect(self.on_error)
        self.youtube_thread.finished.connect(self.download_finished)
        self.youtube_thread.start()
    
    def start_regular_download(self, url: str, save_location: str):
        """Start regular download."""
        file_name = url.split("/")[-1]
        if '?' in file_name:
            file_name = file_name.split('?')[0]
        if not file_name:
            file_name = 'download'
        
        file_path = os.path.join(save_location, file_name)
        
        # Handle duplicate files
        counter = 1
        base_path = file_path
        while os.path.exists(file_path):
            name, ext = os.path.splitext(base_path) 
            file_path = f"{name}_{counter}{ext}"
            counter += 1
        
        self.progress_bar.setValue(0)
        self.download_button.setEnabled(False)
        self.download_button.setText("Downloading...")
        
        self.download_thread = DownloadThread(url, file_path)
        self.download_thread.progress_signal.connect(self.update_progress)
        self.download_thread.status_signal.connect(self.update_status)
        self.download_thread.speed_signal.connect(self.update_speed)
        self.download_thread.size_signal.connect(self.update_size)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.start()
    
    def update_progress(self, progress):
        """Update progress bar."""
        self.progress_bar.setValue(progress)
    
    def update_status(self, message):
        """Update status bar."""
        self.status_bar.showMessage(message)
    
    def update_speed(self, speed):
        """Update download speed."""
        self.download_info.update_info(speed=speed)
    
    def update_size(self, downloaded, total):
        """Update download size info."""
        if total > 0 and downloaded > 0:
            if hasattr(self, 'download_thread') and self.download_thread.start_time:
                elapsed = time.time() - self.download_thread.start_time
                if elapsed > 0:
                    speed = downloaded / elapsed
                    remaining_bytes = total - downloaded
                    time_remaining = remaining_bytes / speed if speed > 0 else 0
                    self.download_info.update_info(size=total, time_remaining=time_remaining)
    
    def on_error(self, error_msg: str):
        """Handle download errors."""
        self.status_bar.showMessage(f"Error: {error_msg}")
        self.download_button.setEnabled(True)
        self.download_button.setText("Start Download")
        QMessageBox.warning(self, "Download Error", error_msg)
    
    def download_finished(self):
        """Handle download completion."""
        # Clean up download threads
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.wait(1000)  # Wait up to 1 second for thread to finish
        if self.youtube_thread and self.youtube_thread.isRunning():
            self.youtube_thread.wait(1000)
            
        self.download_button.setEnabled(True)
        self.download_button.setText("Start Download")
        self.url_widget.clear()
        
        if self.video_preview_group.isVisible():
            self.thumbnail_widget.clear()
            self.video_info_widget.clear()
            self.quality_widget.clear()
            self.video_preview_group.setVisible(False)
            self.current_video_info = None
        
        # Resize window to compact size
        self.resize_window_compact()
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About FKDM",
            "<h3>FKDM Download Manager</h3>"
            "<p>Simple, fast download manager with YouTube support.</p>"
            "<p>Version 2.0</p>"
        )


def runApp():
    """Run the FKDM application."""
    app = QApplication(sys.argv)
    fkdm = FKDMApp()
    fkdm.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    runApp()