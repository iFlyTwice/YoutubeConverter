import customtkinter as ctk
from components.buttons import AnimatedButton
from components.download_card import DownloadCard
from PIL import Image
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
from utils.ui_helper import UIHelper
from utils.browser_automation import BrowserAutomation
from utils.cookie_manager import cookie_manager

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
    def __init__(self, master, app=None, **kwargs):
        self.app = app  # Store app reference before super().__init__
        super().__init__(master, **kwargs)
        self.settings_manager = SettingsManager()
        self.browser_automation = BrowserAutomation()
        
        # Configure the frame
        self.configure(fg_color=DARKER_COLOR)

        # URL Entry frame with centered content
        self.url_frame = ctk.CTkFrame(self, fg_color=DARKER_COLOR)
        self.url_frame.pack(fill="x", padx=10, pady=(20, 10))
        
        # Create a sub-frame for all controls to keep them together
        self.controls_frame = ctk.CTkFrame(self.url_frame, fg_color=DARKER_COLOR)
        self.controls_frame.pack(fill="x", expand=True)
        
        # URL Entry with validation
        self.url_entry = ctk.CTkEntry(
            self.controls_frame,
            placeholder_text="Enter YouTube URL",
            height=45,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            fg_color="#1e1e1e",
            border_color="#2d2d2d",
            text_color="#ffffff",
            corner_radius=10
        )
        self.url_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.url_entry.bind('<KeyRelease>', self._on_url_change)  # Add URL change handler
        
        # Create a frame for the action buttons to keep them together
        self.buttons_frame = ctk.CTkFrame(self.controls_frame, fg_color=DARKER_COLOR)
        self.buttons_frame.pack(side="left", padx=5)
        
        # Paste button
        self.paste_btn = ctk.CTkButton(
            self.buttons_frame,
            text="📋",
            width=45,
            height=45,
            fg_color="#2d2d2d",
            hover_color="#363636",
            corner_radius=10,
            font=ctk.CTkFont(size=16),
            command=self.paste_url
        )
        self.paste_btn.pack(side="left", padx=2)
        
        # Download Button
        self.download_btn = ctk.CTkButton(
            self.buttons_frame,
            text="📥",
            width=45,
            height=45,
            fg_color="#2d2d2d",
            hover_color="#363636",
            corner_radius=10,
            font=ctk.CTkFont(size=16),
            command=self.start_download
        )
        self.download_btn.pack(side="left", padx=2)
        
        # Preview Frame with modern card design
        self.preview_frame = ctk.CTkFrame(
            self,
            fg_color="#1e1e1e",
            corner_radius=15
        )
        self.preview_frame.pack(fill="x", padx=40, pady=30)
        
        # Create inner preview card with dynamic sizing
        self.preview_card = ctk.CTkFrame(
            self.preview_frame,
            fg_color="#252525",
            corner_radius=12
        )
        self.preview_card.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Thumbnail frame with dynamic sizing
        self.thumbnail_frame = ctk.CTkFrame(
            self.preview_card,
            fg_color="transparent"
        )
        self.thumbnail_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # Thumbnail label (will hold the image)
        self.thumbnail_label = ctk.CTkLabel(
            self.thumbnail_frame,
            text="",
            image=None
        )
        self.thumbnail_label.pack(expand=True)
        
        # Video info frame
        self.video_info_frame = ctk.CTkFrame(
            self.preview_card,
            fg_color="transparent"
        )
        self.video_info_frame.pack(fill="x", padx=15, pady=5)
        
        # Title label
        self.title_label = ctk.CTkLabel(
            self.video_info_frame,
            text="Enter a YouTube URL to see preview",
            text_color="#ffffff",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            wraplength=500,
            justify="left"
        )
        self.title_label.pack(anchor="w")
        
        # Channel and duration frame
        self.metadata_frame = ctk.CTkFrame(
            self.video_info_frame,
            fg_color="transparent"
        )
        self.metadata_frame.pack(fill="x", pady=(5, 0))
        
        # Channel name
        self.channel_label = ctk.CTkLabel(
            self.metadata_frame,
            text="",
            text_color="#aaaaaa",
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.channel_label.pack(side="left")
        
        # Duration
        self.duration_label = ctk.CTkLabel(
            self.metadata_frame,
            text="",
            text_color="#aaaaaa",
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.duration_label.pack(side="right")

        # Format and Quality frame
        self.format_controls_frame = ctk.CTkFrame(self, fg_color=DARKER_COLOR)
        self.format_controls_frame.pack(fill="x", padx=40, pady=(0, 30))
        
        # Center container for format and quality controls
        self.format_controls_center = ctk.CTkFrame(self.format_controls_frame, fg_color=DARKER_COLOR)
        self.format_controls_center.pack(expand=True, anchor="center")
        
        # Format dropdown
        self.format_label = ctk.CTkLabel(
            self.format_controls_center,
            text="Format:",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color="#ffffff"
        )
        self.format_label.pack(side="left", padx=(0, 5))
        
        self.format_var = ctk.StringVar(value="MP4")
        self.format_dropdown = ctk.CTkOptionMenu(
            self.format_controls_center,
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
            self.format_controls_center,
            text="Quality:",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color="#ffffff"
        )
        self.quality_label.pack(side="left", padx=(0, 5))
        
        self.quality_var = ctk.StringVar(value="Highest")
        self.quality_dropdown = ctk.CTkOptionMenu(
            self.format_controls_center,
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

    def update_preview(self, video_info):
        """Update the preview card with video information"""
        if not video_info:
            self.thumbnail_label.configure(image=None)
            self.title_label.configure(text="Enter a YouTube URL to see preview")
            self.channel_label.configure(text="")
            self.duration_label.configure(text="")
            return
            
        try:
            # Get thumbnail
            if 'thumbnail_url' in video_info:
                response = requests.get(video_info['thumbnail_url'])
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content))
                    
                    # Calculate the aspect ratio of the original image
                    aspect_ratio = img.width / img.height
                    
                    # Get window dimensions
                    window_width = self.winfo_width()
                    window_height = self.winfo_height()
                    
                    # Set minimum and maximum dimensions
                    min_width = 400
                    max_width = 1200
                    min_height = 225  # 16:9 aspect ratio minimum
                    max_height = 675  # 16:9 aspect ratio maximum
                    
                    # Calculate target width (70% of window width, within bounds)
                    target_width = min(max_width, max(min_width, int(window_width * 0.7)))
                    
                    # Calculate target height based on aspect ratio
                    target_height = int(target_width / aspect_ratio)
                    
                    # Ensure height is within bounds
                    if target_height > max_height:
                        target_height = max_height
                        target_width = int(target_height * aspect_ratio)
                    elif target_height < min_height:
                        target_height = min_height
                        target_width = int(target_height * aspect_ratio)
                    
                    # Add padding to prevent content from being cut off
                    padding_x = 40
                    padding_y = 30
                    
                    # Resize image maintaining aspect ratio
                    img = UIHelper.resize_image(img, (target_width, target_height))
                    
                    # Create CTkImage with the calculated size
                    ctk_img = ctk.CTkImage(light_image=img, dark_image=img, 
                                         size=(target_width, target_height))
                    
                    # Update thumbnail label
                    self.thumbnail_label.configure(image=ctk_img)
                    self.current_thumbnail = ctk_img
                    
                    # Update frame sizes with padding
                    self.thumbnail_frame.configure(width=target_width + padding_x, height=target_height)
                    self.preview_frame.configure(width=target_width + padding_x * 2, 
                                              height=target_height + padding_y * 2 + 120)  # Add padding for text
                    
                    # Ensure the preview frame maintains its size
                    self.preview_frame.pack_propagate(False)
            
            # Update other video information
            title = video_info.get('title', 'Unknown Title')
            channel = video_info.get('channel', 'Unknown Channel')
            duration = video_info.get('duration', 0)
            
            # Format duration
            duration_str = str(timedelta(seconds=int(duration))) if duration else "Unknown duration"
            if duration_str.startswith('0:'):
                duration_str = duration_str[2:]  # Remove leading 0: if less than an hour
            
            self.title_label.configure(text=title)
            self.channel_label.configure(text=channel)
            self.duration_label.configure(text=duration_str)
            
        except Exception as e:
            logging.error(f"Error updating preview: {str(e)}")
            self.title_label.configure(text="Error loading video preview")
            
    def _on_url_change(self, event=None):
        """Handle URL changes and update preview"""
        url = self.url_entry.get().strip()
        if not url:
            self.update_preview(None)
            return
            
        try:
            # Check if we need to refresh cookies
            if not os.path.exists(cookie_manager.cookie_file) or os.path.getsize(cookie_manager.cookie_file) < 100:
                # Run browser automation to get fresh cookies
                if not self.browser_automation._setup_driver():
                    logging.error("Failed to setup browser automation")
                    return
                cookies = self.browser_automation.get_youtube_cookies()
                if cookies:
                    with open(cookie_manager.cookie_file, 'w') as f:
                        f.write(cookies)
                if self.browser_automation.driver:
                    self.browser_automation.driver.quit()
            
            # Now try to get video info with cookies
            video_info = api.get_video_info(url)
            if video_info:
                # Transform video info for preview
                preview_info = {
                    'title': video_info.get('title', 'No title available'),
                    'author': video_info.get('uploader', video_info.get('channel', 'Unknown channel')),
                    'length': video_info.get('duration', 0),
                    'thumbnail_url': video_info.get('thumbnail', video_info.get('thumbnail_url'))
                }
                self.update_preview(preview_info)
            else:
                self.update_preview(None)
        except Exception as e:
            logging.error(f"Error updating preview: {e}")
            self.update_preview(None)
            # If error is about cookies, try to refresh them
            if "Sign in to confirm you're not a bot" in str(e):
                cookie_manager.clear_cookies()  # Clear existing cookies
                # Trigger URL change again to get fresh cookies
                self.after(1000, lambda: self._on_url_change(event))

    @staticmethod
    def open(parent_frame, app=None):
        """Open the main page"""
        main_page = MainPage(parent_frame)
        main_page.pack(fill="both", expand=True)
        return main_page
