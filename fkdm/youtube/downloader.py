"""
YouTube video downloader module using yt-dlp.
Provides functionality for downloading YouTube videos with quality selection.
"""

import os
import json
import subprocess
from typing import Dict, List, Optional, Tuple
from PyQt5.QtCore import QThread, pyqtSignal
import requests
from io import BytesIO
from PIL import Image


class YouTubeInfo:
    """
    Container for YouTube video information.
    """
    
    def __init__(self, info_dict: Dict):
        """
        Initialize with video information dictionary from yt-dlp.
        
        Args:
            info_dict: Dictionary containing video metadata
        """
        self.url = info_dict.get('webpage_url', '')
        self.title = info_dict.get('title', 'Unknown Title')
        self.duration = info_dict.get('duration', 0)
        self.thumbnail = info_dict.get('thumbnail', '')
        self.uploader = info_dict.get('uploader', 'Unknown')
        self.view_count = info_dict.get('view_count', 0)
        self.description = info_dict.get('description', '')
        self.formats = info_dict.get('formats', [])
        self.filesize = info_dict.get('filesize', 0)
        
    def get_duration_string(self) -> str:
        """
        Convert duration in seconds to readable format.
        
        Returns:
            Formatted duration string (HH:MM:SS or MM:SS)
        """
        if self.duration:
            hours = self.duration // 3600
            minutes = (self.duration % 3600) // 60
            seconds = self.duration % 60
            
            if hours > 0:
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                return f"{minutes:02d}:{seconds:02d}"
        return "00:00"
    
    def get_available_qualities(self) -> List[Tuple[str, str]]:
        """
        Get list of available video qualities.
        
        Returns:
            List of tuples (format_id, quality_description)
        """
        qualities = []
        seen = set()
        
        for fmt in self.formats:
            if fmt.get('vcodec') != 'none':  # Has video
                height = fmt.get('height', 0)
                fps = fmt.get('fps', 30)
                format_id = fmt.get('format_id', '')
                ext = fmt.get('ext', 'mp4')
                filesize = fmt.get('filesize', 0)
                
                if height and height not in seen:
                    seen.add(height)
                    quality_str = f"{height}p"
                    if fps > 30:
                        quality_str += f" {fps}fps"
                    if filesize:
                        size_mb = filesize / (1024 * 1024)
                        quality_str += f" ({size_mb:.1f} MB)"
                    quality_str += f" .{ext}"
                    qualities.append((format_id, quality_str))
        
        # Sort by height (quality) in descending order
        qualities.sort(key=lambda x: int(x[1].split('p')[0]), reverse=True)
        
        # Add best quality option at the top
        qualities.insert(0, ('best', 'Best Quality (Video + Audio)'))
        qualities.append(('bestaudio', 'Audio Only (Best Quality)'))
        
        return qualities


class YouTubeDownloadThread(QThread):
    """
    Background thread for downloading YouTube videos using yt-dlp.
    """
    
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str)
    info_signal = pyqtSignal(object)
    error_signal = pyqtSignal(str)
    speed_signal = pyqtSignal(float)
    
    def __init__(self, url: str, output_path: str, format_id: str = 'best'):
        """
        Initialize YouTube download thread.
        
        Args:
            url: YouTube video URL
            output_path: Path to save the downloaded file
            format_id: Format ID for quality selection
        """
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.format_id = format_id
        self.process = None
        
    def run(self):
        """
        Execute the download process using yt-dlp.
        """
        try:
            # Prepare yt-dlp command
            cmd = [
                'yt-dlp',
                '--progress',
                '--newline',
                '--no-warnings',
                '-o', self.output_path,
                self.url
            ]
            
            # Add format selection
            if self.format_id == 'best':
                cmd.extend(['-f', 'bestvideo+bestaudio/best'])
                cmd.extend(['--merge-output-format', 'mp4'])
            elif self.format_id == 'bestaudio':
                cmd.extend(['-f', 'bestaudio'])
                cmd.extend(['--extract-audio', '--audio-format', 'mp3'])
            else:
                cmd.extend(['-f', self.format_id])
            
            self.status_signal.emit("Starting YouTube download...")
            self.status_signal.emit(f"Command: {' '.join(cmd)}")
            
            # Run yt-dlp process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Combine stderr with stdout
                universal_newlines=True,
                bufsize=1
            )
            
            # Parse output for progress
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    line = line.strip()
                    self.parse_progress(line)
                    # Also emit raw output for debugging
                    if '[download]' not in line:
                        self.status_signal.emit(line)
            
            # Wait for process to complete
            self.process.wait()
            
            if self.process.returncode == 0:
                self.status_signal.emit("Download completed successfully!")
                self.progress_signal.emit(100)
            else:
                self.error_signal.emit(f"Download failed with return code: {self.process.returncode}")
                
        except FileNotFoundError:
            self.error_signal.emit("yt-dlp not found. Please install it using: pip install yt-dlp")
        except Exception as e:
            self.error_signal.emit(f"Download error: {str(e)}")
    
    def parse_progress(self, line: str):
        """
        Parse yt-dlp output line for progress information.
        
        Args:
            line: Output line from yt-dlp
        """
        try:
            if '[download]' in line:
                if '%' in line:
                    # Extract percentage
                    parts = line.split()
                    for part in parts:
                        if '%' in part:
                            percent_str = part.replace('%', '')
                            try:
                                percent = float(percent_str)
                                self.progress_signal.emit(int(percent))
                            except ValueError:
                                pass
                    
                    # Extract speed if available
                    if 'at' in line and '/s' in line:
                        speed_part = line.split('at')[1].split('/s')[0].strip()
                        speed_value = self.parse_speed(speed_part)
                        if speed_value:
                            self.speed_signal.emit(speed_value)
                
                # Update status
                if 'Destination:' in line:
                    self.status_signal.emit("Downloading video...")
                elif 'Merging' in line:
                    self.status_signal.emit("Merging video and audio...")
                elif 'Deleting' in line:
                    self.status_signal.emit("Cleaning up temporary files...")
                    
        except Exception:
            pass  # Ignore parsing errors
    
    def parse_speed(self, speed_str: str) -> Optional[float]:
        """
        Parse speed string to bytes per second.
        
        Args:
            speed_str: Speed string like "1.5MiB" or "500KiB"
            
        Returns:
            Speed in bytes per second, or None if parsing fails
        """
        try:
            speed_str = speed_str.strip()
            if 'MiB' in speed_str:
                return float(speed_str.replace('MiB', '')) * 1024 * 1024
            elif 'KiB' in speed_str:
                return float(speed_str.replace('KiB', '')) * 1024
            elif 'B' in speed_str:
                return float(speed_str.replace('B', ''))
        except:
            return None
    
    def stop(self):
        """
        Stop the download process if running.
        """
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.status_signal.emit("Download cancelled")


def get_video_info(url: str) -> Optional[YouTubeInfo]:
    """
    Fetch video information without downloading.
    
    Args:
        url: YouTube video URL
        
    Returns:
        YouTubeInfo object or None if failed
    """
    try:
        cmd = [
            'yt-dlp',
            '--dump-json',
            '--no-warnings',
            url
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            info_dict = json.loads(result.stdout)
            return YouTubeInfo(info_dict)
        else:
            return None
            
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        return None


def download_thumbnail(thumbnail_url: str) -> Optional[bytes]:
    """
    Download thumbnail image from URL.
    
    Args:
        thumbnail_url: URL of the thumbnail image
        
    Returns:
        Image bytes or None if failed
    """
    try:
        response = requests.get(thumbnail_url, timeout=5)
        if response.status_code == 200:
            return response.content
        return None
    except:
        return None


def is_youtube_url(url: str) -> bool:
    """
    Check if the given URL is a YouTube URL.
    
    Args:
        url: URL to check
        
    Returns:
        True if YouTube URL, False otherwise
    """
    youtube_domains = [
        'youtube.com',
        'youtu.be',
        'www.youtube.com',
        'm.youtube.com'
    ]
    
    return any(domain in url.lower() for domain in youtube_domains)