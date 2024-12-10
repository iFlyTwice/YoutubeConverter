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
        self.active_page = "home"  # Track current active page
        
        # Configure the frame
        self.configure(fg_color=DARKER_COLOR)

        # Create YouPro label frame
        self.youpro_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.youpro_frame.pack(fill="x", padx=20, pady=(15, 10))
        
        # Add YouPro text
        self.youpro_label = ctk.CTkLabel(
            self.youpro_frame,
            text="YouPro",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color="#ffffff"
        )
        self.youpro_label.pack(anchor="w")
        
        # Add yellow underline
        self.youpro_underline = ctk.CTkFrame(
            self.youpro_frame,
            height=3,
            width=80,
            fg_color="#FFB74D"
        )
        self.youpro_underline.pack(anchor="w", pady=(2, 0))

        # Create loading overlay
        self.loading_overlay = ctk.CTkFrame(self, fg_color="#1e1e1e")
        self.loading_label = ctk.CTkLabel(
            self.loading_overlay,
            text="Loading...",
            font=ctk.CTkFont(family="Segoe UI", size=16),
            text_color="#ffffff"
        )
        self.loading_label.pack(expand=True)
        
        # URL Entry frame
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
        
        # Home page container
        self.home_frame = ctk.CTkFrame(
            master=self,
            fg_color="transparent"
        )

        # Welcome header
        self.header_label = UIHelper.create_label(
            self.home_frame,
            text="Welcome to YouTube Clipping",
            font=("Segoe UI", 24, "bold")
        )
        self.header_label.pack(pady=(30, 20))

        # Description
        self.description_label = UIHelper.create_label(
            self.home_frame,
            text="Convert YouTube videos to MP3 or MP4 with ease.\nClip and customize your favorite moments!",
            font=("Segoe UI", 14),
            justify="center"
        )
        self.description_label.pack(pady=(0, 30))

        # Recent downloads section
        self.recent_frame = ctk.CTkFrame(
            master=self.home_frame,
            fg_color="#1e1e1e",
            corner_radius=15,
            border_width=2,
            border_color="#3f3f3f"
        )
        self.recent_frame.pack(fill="x", padx=20, pady=10)

        self.recent_label = UIHelper.create_label(
            self.recent_frame,
            text="Recent Downloads",
            font=("Segoe UI", 16, "bold")
        )
        self.recent_label.pack(pady=15)

        # Placeholder for recent downloads list
        self.recent_list = ctk.CTkFrame(
            master=self.recent_frame,
            fg_color="transparent"
        )
        self.recent_list.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Preview Frame with modern card design
        self.preview_frame = ctk.CTkFrame(
            self,
            fg_color="#1e1e1e",
            corner_radius=15,
            border_width=2,
            border_color="#3f3f3f"
        )
        self.preview_frame.pack_forget()  # Hide by default
        
        # Create preview card layout
        self.preview_card = ctk.CTkFrame(
            master=self.preview_frame,
            fg_color="#1e1e1e",
            corner_radius=15
        )
        self.preview_card.pack(fill="x", padx=10, pady=10)
        
        # Left side: Thumbnail
        self.left_frame = ctk.CTkFrame(
            master=self.preview_card,
            fg_color="transparent"
        )
        self.left_frame.pack(side="left", fill="y", padx=20, pady=10)

        # Thumbnail
        self.thumbnail_frame = ctk.CTkFrame(
            master=self.left_frame,
            fg_color="transparent",
            width=180,  # Fixed width for thumbnail
            height=120  # Fixed height for thumbnail
        )
        self.thumbnail_frame.pack(side="top")
        self.thumbnail_frame.pack_propagate(False)  # Maintain fixed size
        
        self.thumbnail_label = ctk.CTkLabel(
            master=self.thumbnail_frame,
            text="",
            image=None
        )
        self.thumbnail_label.pack(expand=True, fill="both")

        # Right side: Video information
        self.info_frame = ctk.CTkFrame(
            master=self.preview_card,
            fg_color="transparent"
        )
        self.info_frame.pack(side="left", fill="both", expand=True, padx=(10, 20), pady=10)

        # Video title
        self.title_label = UIHelper.create_label(
            self.info_frame,
            text="Enter a YouTube URL to see preview",
            font=("Segoe UI", 14, "bold"),
            wraplength=300
        )
        self.title_label.pack(side="top", anchor="w", pady=(0, 5))

        # Channel and duration
        self.metadata_frame = ctk.CTkFrame(
            master=self.info_frame,
            fg_color="transparent"
        )
        self.metadata_frame.pack(side="top", fill="x")

        self.channel_label = UIHelper.create_label(
            self.metadata_frame,
            text="",
            font=("Segoe UI", 12),
            text_color="#aaaaaa"
        )
        self.channel_label.pack(side="left")

        self.duration_label = UIHelper.create_label(
            self.metadata_frame,
            text="",
            font=("Segoe UI", 12),
            text_color="#aaaaaa"
        )
        self.duration_label.pack(side="right")

        # Format and quality controls
        self.controls_frame = ctk.CTkFrame(
            master=self.info_frame,
            fg_color="transparent"
        )
        self.controls_frame.pack(side="top", fill="x", pady=(15, 0))

        # Format selection
        self.format_var = ctk.StringVar(value="MP4")
        self.format_menu = UIHelper.create_dropdown(
            self.controls_frame,
            values=["MP4", "MP3"],
            variable=self.format_var,
            width=80
        )
        self.format_menu.pack(side="left", padx=(0, 10))

        # Quality selection
        self.quality_var = ctk.StringVar(value="Highest")
        self.quality_menu = UIHelper.create_dropdown(
            self.controls_frame,
            values=["Highest", "1080p", "720p", "480p", "360p"],
            variable=self.quality_var,
            width=90
        )
        self.quality_menu.pack(side="left")

        # Download progress
        self.progress_frame = ctk.CTkFrame(
            master=self.info_frame,
            fg_color="transparent"
        )
        self.progress_frame.pack(side="top", fill="x", pady=(10, 0))

        # Download button and progress bar in same row
        self.download_button = ctk.CTkButton(
            master=self.progress_frame,
            text="Download",
            font=("Segoe UI", 12),
            width=100,
            height=28,
            fg_color="#404040",
            hover_color="#4a4a4a",
            command=self.start_download
        )
        self.download_button.pack(side="left", pady=(0, 5))

        self.progress_bar = ctk.CTkProgressBar(
            master=self.progress_frame,
            mode="determinate",
            height=5,
            progress_color="#ffb74d"
        )
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=(10, 0))
        self.progress_bar.set(0)

        self.progress_label = UIHelper.create_label(
            self.progress_frame,
            text="",
            font=("Segoe UI", 11),
            text_color="#aaaaaa"
        )
        self.progress_label.pack(side="right", pady=(5, 0))
        
        # Progress bar
        self.bottom_progress_bar = ctk.CTkProgressBar(
            self,
            mode="determinate",
            height=3,
            fg_color="#1e1e1e",
            progress_color="#404040",
            corner_radius=2
        )
        self.bottom_progress_bar.pack(fill="x", padx=40, pady=(30, 0), side="bottom")
        self.bottom_progress_bar.set(0)
        
        # Active downloads
        self.active_downloads = {}
        
        self.show_home_page()  # Show home page by default

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
        """Paste URL from clipboard and process it immediately"""
        try:
            url = self.clipboard_get().strip()
            if url:
                logging.info(f"Pasted URL: {url}")
                self.url_entry.delete(0, 'end')
                self.url_entry.insert(0, url)
                # Switch to converter page and process URL
                self.smooth_transition_to_converter()
                self.process_url(url)
        except Exception as e:
            logging.error(f"Error pasting URL: {e}")
            
    def is_valid_youtube_url(self, url):
        """Check if the URL is a valid YouTube URL"""
        youtube_pattern = r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        video_pattern = r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        youtube_regex = rf'(https?://)?(www\.)?{youtube_pattern}{video_pattern}'
        youtube_regex_match = re.match(youtube_regex, url)
        return bool(youtube_regex_match)

    def process_url(self, url):
        """Process the YouTube URL and update the preview"""
        try:
            logging.info(f"Starting to fetch video info for URL: {url}")
            video_info = self.fetch_video_info(url)
            
            if video_info:
                # Update preview in main thread
                self.after(0, lambda: self.update_preview(video_info))
                self.after(0, self.hide_loading)
            else:
                self.after(0, lambda: self.show_error("Could not fetch video information"))
                self.after(0, self.smooth_transition_to_home)
                
        except Exception as e:
            logging.error(f"Error processing URL: {e}")
            self.after(0, lambda: self.show_error(str(e)))
            self.after(0, self.smooth_transition_to_home)

    def fetch_video_info(self, url):
        """Fetch video information using yt-dlp"""
        try:
            # Extract video info using the YouTube API
            info = api.get_video_info(url)
            
            if not info:
                return None
                
            # Format the video information
            video_info = {
                'id': info.get('id', ''),
                'title': info.get('title', 'Unknown Title'),
                'channel': info.get('author', 'Unknown channel'),
                'duration': info.get('duration', 0),
                'thumbnail_url': info.get('thumbnail', f"https://img.youtube.com/vi/{info.get('id', '')}/maxresdefault.jpg"),
                'formats': info.get('formats', [])
            }
            
            # Show converter page before updating preview
            self.after(0, self.show_converter_page)
            
            # Update the UI with the fetched information
            self.after(0, lambda: self.update_preview(video_info))
            return video_info
            
        except Exception as e:
            logging.error(f"Error fetching video info: {e}")
            self.after(0, lambda: self.show_error("Error fetching video information"))
            return None

    def show_error(self, message):
        """Show error message in the preview frame"""
        self.title_label.configure(text=message)
        self.channel_label.configure(text="")
        self.duration_label.configure(text="")
        self.thumbnail_label.configure(image=None)
        
    def update_preview(self, video_info):
        """Update the preview card with video information"""
        try:
            if video_info is None:
                logging.error("update_preview received None video_info")
                return
                
            logging.info("Updating preview UI with video information...")
            
            # Update text info first for immediate feedback
            title = video_info.get('title', 'No title available')
            self.title_label.configure(text=title)
            
            channel = video_info.get('channel', 'Unknown Channel')
            self.channel_label.configure(text=channel)
            
            duration = timedelta(seconds=int(video_info.get('duration', 0)))
            self.duration_label.configure(text=str(duration))
            
            # Update thumbnail in background
            def load_thumbnail():
                thumbnail_url = video_info.get('thumbnail_url')
                if thumbnail_url:
                    try:
                        response = requests.get(thumbnail_url)
                        img_data = Image.open(BytesIO(response.content))
                        img_data = img_data.resize((180, 120), Image.Resampling.LANCZOS)
                        thumbnail = ctk.CTkImage(img_data, size=(180, 120))
                        self.after(0, lambda: self.thumbnail_label.configure(image=thumbnail, text=""))
                    except Exception as e:
                        logging.error(f"Error loading thumbnail: {e}")
                        self.after(0, lambda: self.thumbnail_label.configure(text="Thumbnail unavailable"))
            
            threading.Thread(target=load_thumbnail, daemon=True).start()
            
            # Stop progress animation
            self.progress_bar.stop()
            self.progress_bar.configure(mode="determinate")
            
            logging.info("Preview update completed successfully")
            
        except Exception as e:
            logging.error(f"Error updating preview: {e}")
            self.show_error("Error updating preview")
            
    def show_loading(self, message="Loading..."):
        """Show loading overlay with message"""
        self.loading_label.configure(text=message)
        self.loading_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.loading_overlay.lift()
        self.update_idletasks()
        
    def hide_loading(self):
        """Hide loading overlay"""
        self.loading_overlay.place_forget()
        self.update_idletasks()

    def smooth_transition_to_converter(self):
        """Smoothly transition from home to converter page"""
        # First show loading
        self.show_loading("Loading video information...")
        
        # Pre-configure preview frame
        self.title_label.configure(text="Loading...")
        self.channel_label.configure(text="Please wait...")
        self.duration_label.configure(text="")
        self.thumbnail_label.configure(image=None, text="Loading thumbnail...")
        
        # Pack preview frame before unpacking home
        if not self.preview_frame.winfo_ismapped():
            self.preview_frame.pack(fill="x", padx=20, pady=10)
        
        # Start progress bar animation
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        
        # Unpack home frame
        self.home_frame.pack_forget()
        self.active_page = "converter"
        
        # Update UI
        self.update_idletasks()
        
    def smooth_transition_to_home(self):
        """Smoothly transition from converter to home page"""
        # Show loading
        self.show_loading("Returning to home...")
        
        # Stop progress bar
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        
        # Pack home before unpacking preview
        self.home_frame.pack(fill="both", expand=True)
        self.preview_frame.pack_forget()
        self.active_page = "home"
        
        # Hide loading
        self.hide_loading()
        
    def _on_url_change(self, event=None):
        """Handle URL changes in the entry field"""
        url = self.url_entry.get().strip()
        
        # Quick validation of URL format
        if not url:
            return
            
        # Show loading state immediately if URL looks valid
        if 'youtube.com' in url or 'youtu.be' in url:
            # Smooth transition to converter page
            self.smooth_transition_to_converter()
            
            # Start fetching in background
            threading.Thread(target=lambda: self.process_url(url), daemon=True).start()
        else:
            self.show_error("Invalid YouTube URL")
            self.smooth_transition_to_home()

    def show_home_page(self):
        self.preview_frame.pack_forget()
        self.home_frame.pack(fill="both", expand=True)
        self.active_page = "home"

    def show_converter_page(self):
        """Show the converter page with video preview"""
        # Hide home page
        self.home_frame.pack_forget()
        
        # Show preview frame
        self.preview_frame.pack(fill="x", padx=20, pady=10)
        
        # Reset progress
        self.progress_bar.set(0)
        self.progress_label.configure(text="")
        
        self.active_page = "converter"

    @staticmethod
    def open(parent_frame, app=None):
        """Open the main page"""
        main_page = MainPage(parent_frame)
        main_page.pack(fill="both", expand=True)
        return main_page
