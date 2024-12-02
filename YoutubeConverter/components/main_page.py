import customtkinter as ctk
from components.buttons import AnimatedButton
from components.download_card import DownloadCard
from PIL import Image, ImageTk
import urllib.request
from io import BytesIO
import threading
import re
import os
from datetime import timedelta
import humanize
import logging
import json
from datetime import datetime
import requests
from services.youtube_api import api
from utils.widget_manager import manager as widget_manager
from utils.settings_manager import SettingsManager

# Set up logging
log_dir = os.path.join(os.path.expanduser("~"), "Downloads", "YouTube Converter", "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "url_history.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Colors
DARKER_COLOR = "#1a1a1a"
ACCENT_COLOR = "#3d3d3d"
HOVER_COLOR = "#4d4d4d"
TEXT_COLOR = "#ffffff"
BG_COLOR = "#2d2d2d"
DISABLED_COLOR = "#cccccc"

class MainPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.settings_manager = SettingsManager()
        
        # Configure the frame
        self.configure(fg_color=DARKER_COLOR)

        # URL Entry frame with centered content
        self.url_frame = ctk.CTkFrame(self, fg_color=DARKER_COLOR)
        self.url_frame.pack(fill="x", padx=40, pady=(20, 10))
        
        # URL Entry
        self.url_entry = ctk.CTkEntry(
            self.url_frame,
            placeholder_text="Enter YouTube URL",
            height=45,
            width=600,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            fg_color="#1e1e1e",
            border_color="#2d2d2d",
            text_color="#ffffff",
            corner_radius=10
        )
        self.url_entry.pack(side="left", padx=(0, 10), expand=True)
        
        # Paste button
        self.paste_btn = ctk.CTkButton(
            self.url_frame,
            text="📋",
            width=45,
            height=45,
            fg_color="#2d2d2d",
            hover_color="#363636",
            corner_radius=10,
            font=ctk.CTkFont(size=20),
            command=self.paste_url
        )
        self.paste_btn.pack(side="left", padx=(0, 10))
        
        # Download Button
        self.download_btn = ctk.CTkButton(
            self.url_frame,
            text="Download",
            width=120,
            height=45,
            fg_color="#2d2d2d",
            hover_color="#363636",
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            command=self.start_download
        )
        self.download_btn.pack(side="left")
        
        # Preview Frame
        self.preview_frame = ctk.CTkFrame(
            self,
            fg_color="#1e1e1e",
            height=250,
            corner_radius=15
        )
        self.preview_frame.pack(fill="x", padx=40, pady=30)
        self.preview_frame.pack_propagate(False)
        
        # Preview placeholder
        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="Video preview will appear here",
            text_color="#4d4d4d",
            font=ctk.CTkFont(family="Segoe UI", size=14)
        )
        self.preview_label.pack(expand=True)
        
        # Format and Quality frame
        self.controls_frame = ctk.CTkFrame(self, fg_color=DARKER_COLOR)
        self.controls_frame.pack(fill="x", padx=40, pady=(0, 30))
        
        # Center container for format and quality controls
        self.controls_center = ctk.CTkFrame(self.controls_frame, fg_color=DARKER_COLOR)
        self.controls_center.pack(expand=True, anchor="center")
        
        # Format dropdown
        self.format_label = ctk.CTkLabel(
            self.controls_center,
            text="Format:",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color="#ffffff"
        )
        self.format_label.pack(side="left", padx=(0, 5))
        
        self.format_var = ctk.StringVar(value="MP4")
        self.format_dropdown = ctk.CTkOptionMenu(
            self.controls_center,
            values=["MP4", "MP3"],
            variable=self.format_var,
            fg_color="#2d2d2d",
            button_color="#363636",
            button_hover_color="#404040",
            width=100,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        self.format_dropdown.pack(side="left", padx=(0, 30))
        
        # Quality dropdown
        self.quality_label = ctk.CTkLabel(
            self.controls_center,
            text="Quality:",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color="#ffffff"
        )
        self.quality_label.pack(side="left", padx=(0, 5))
        
        self.quality_var = ctk.StringVar(value="Highest")
        self.quality_dropdown = ctk.CTkOptionMenu(
            self.controls_center,
            values=["Highest", "1080p", "720p", "480p", "360p"],
            variable=self.quality_var,
            fg_color="#2d2d2d",
            button_color="#363636",
            button_hover_color="#404040",
            width=100,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        self.quality_dropdown.pack(side="left")
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self,
            mode="determinate",
            height=3,
            fg_color="#1e1e1e",
            progress_color="#404040",
            corner_radius=2
        )
        self.progress_bar.pack(fill="x", padx=40, pady=(30, 0), side="bottom")
        self.progress_bar.set(0)
        
        # Active downloads
        self.active_downloads = {}
        
    def start_download(self):
        """Start the download process"""
        url = self.url_entry.get().strip()
        if not url:
            return
            
        try:
            # Get video info
            video_info = api.get_video_info(url)
            if not video_info:
                return
            
            # Create download card
            download_card = DownloadCard(
                self,
                title=video_info['title'],
                on_cancel=lambda: self.cancel_download(url)
            )
            download_card.pack(fill="x", padx=40, pady=10)
            self.active_downloads[url] = download_card
            
            # Start download in background thread
            thread = threading.Thread(
                target=self._download_thread,
                args=(url, video_info),
                daemon=True
            )
            thread.start()
        except Exception as e:
            logging.error(f"Error starting download: {e}")

    def _download_thread(self, url: str, video_info: dict):
        """Handle download in background thread"""
        try:
            # Get selected format and quality
            format = self.format_var.get().lower()
            quality = self.quality_var.get()
            
            # Get output path from settings
            output_path = os.path.join(os.path.expanduser("~"), "Downloads", "YouTube Converter", "downloads")
            os.makedirs(output_path, exist_ok=True)
            
            # Progress callback
            def progress_callback(progress: float):
                if url in self.active_downloads:
                    card = self.active_downloads[url]
                    if not card.is_cancelled:
                        card.update_progress(
                            progress,
                            f"Downloading... {progress:.1f}%"
                        )
            
            # Download the video
            output_file = api.download_video(
                url,
                output_path,
                format=format,
                quality=quality,
                progress_callback=progress_callback
            )
            
            # Update download card on completion
            if url in self.active_downloads:
                card = self.active_downloads[url]
                if not card.is_cancelled:
                    card.update_progress(100, "Download complete!")
                    
        except Exception as e:
            logging.error(f"Error in download thread: {e}")
            if url in self.active_downloads:
                card = self.active_downloads[url]
                card.update_progress(0, f"Error: {str(e)}")

    def cancel_download(self, url: str):
        """Cancel an active download"""
        if url in self.active_downloads:
            self.active_downloads[url].update_progress(
                0, "Download cancelled"
            )
            # Thread will check cancelled flag and stop
            
    def paste_url(self):
        """Paste URL from clipboard"""
        try:
            url = self.clipboard_get()
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, url)
        except:
            pass

    @staticmethod
    def open(parent_frame):
        """Open the main page"""
        main_page = MainPage(parent_frame)
        main_page.pack(fill="both", expand=True)
        return main_page
