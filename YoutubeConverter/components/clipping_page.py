import customtkinter as ctk
from ui_helper import UIHelper
from PIL import Image
import urllib.request
from io import BytesIO
import threading
import logging
import requests
from services.youtube_api import api
from utils.cookie_manager import cookie_manager
import os

# Colors
DARKER_COLOR = "#1a1a1a"
ACCENT_COLOR = "#3d3d3d"
HOVER_COLOR = "#4d4d4d"
TEXT_COLOR = "#ffffff"
BG_COLOR = "#2d2d2d"

class ClippingPage(ctk.CTkFrame):
    def __init__(self, master, app=None, on_back_click=None, **kwargs):
        # Store parameters before super().__init__
        self.app = app
        self.on_back_click = on_back_click
        # Remove app and on_back_click from kwargs
        kwargs.pop('app', None)
        kwargs.pop('on_back_click', None)
        super().__init__(master, **kwargs)
        
        # Configure the frame
        self.configure(fg_color=DARKER_COLOR)
        
        # Create header with back button if needed
        self.header = ctk.CTkFrame(self, fg_color="#232323", height=50)
        self.header.pack(fill="x", padx=10, pady=10)
        
        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color=DARKER_COLOR)
        self.main_container.pack(fill="both", expand=True, padx=15, pady=15)

        # URL Entry frame with centered content
        self.url_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=DARKER_COLOR,
        )
        self.url_frame.pack(fill="x", pady=(10, 20))
        
        # URL Entry with validation
        self.url_entry = ctk.CTkEntry(
            self.url_frame,
            placeholder_text="Enter YouTube URL to clip",
            height=45,
            font=("Segoe UI", 14)
        )
        self.url_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.url_entry.bind('<KeyRelease>', self._on_url_change)
        
        # Paste button
        self.paste_btn = ctk.CTkButton(
            self.url_frame,
            text="📋",
            width=45,
            height=45,
            command=self.paste_url,
            font=("Segoe UI", 16)
        )
        self.paste_btn.pack(side="left", padx=5)

        # Home page container
        self.home_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent",
        )
        self.home_frame.pack(fill="both", expand=True)

        # Welcome header
        title_frame = ctk.CTkFrame(self.home_frame, fg_color="transparent")
        title_frame.pack(pady=(30, 30))
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="Video Clipping",
            font=("Segoe UI", 24, "bold"),
            text_color=TEXT_COLOR
        )
        title_label.pack()
        
        desc_label = ctk.CTkLabel(
            title_frame,
            text="Clip and customize your favorite moments from YouTube videos!",
            font=("Segoe UI", 14),
            text_color="#888888"
        )
        desc_label.pack()

        # Preview Frame
        self.preview_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="#1e1e1e",
        )
        self.preview_frame.pack_forget()  # Hide by default

        # Video preview section
        self.video_frame = ctk.CTkFrame(
            self.preview_frame,
            fg_color="transparent",
        )
        self.video_frame.pack(fill="x", padx=20, pady=15)

        # Thumbnail frame
        self.thumbnail_frame = ctk.CTkFrame(
            self.video_frame,
            fg_color="transparent",
            width=320,
            height=180
        )
        self.thumbnail_frame.pack(pady=10)
        self.thumbnail_frame.pack_propagate(False)

        self.thumbnail_label = ctk.CTkLabel(
            self.thumbnail_frame,
            text="",
            image=None
        )
        self.thumbnail_label.pack(expand=True, fill="both")

        # Video title
        self.title_label = ctk.CTkLabel(
            self.video_frame,
            text="Enter a YouTube URL to start clipping",
            font=("Segoe UI", 14, "bold"),
            wraplength=400
        )
        self.title_label.pack(pady=5)

        # Time selection frame
        self.time_frame = ctk.CTkFrame(
            self.preview_frame,
            fg_color="transparent",
        )
        self.time_frame.pack(fill="x", padx=20, pady=10)

        # Start time
        self.start_frame = ctk.CTkFrame(
            self.time_frame,
            fg_color="transparent",
        )
        self.start_frame.pack(side="left", padx=10)

        ctk.CTkLabel(
            self.start_frame,
            text="Start Time",
            font=("Segoe UI", 12)
        ).pack()

        self.start_time = ctk.CTkEntry(
            self.start_frame,
            placeholder_text="00:00",
            width=80,
            height=30
        )
        self.start_time.pack(pady=5)

        # End time
        self.end_frame = ctk.CTkFrame(
            self.time_frame,
            fg_color="transparent",
        )
        self.end_frame.pack(side="left", padx=10)

        ctk.CTkLabel(
            self.end_frame,
            text="End Time",
            font=("Segoe UI", 12)
        ).pack()

        self.end_time = ctk.CTkEntry(
            self.end_frame,
            placeholder_text="00:00",
            width=80,
            height=30
        )
        self.end_time.pack(pady=5)

        # Clip button
        self.clip_button = ctk.CTkButton(
            self.preview_frame,
            text="Create Clip",
            font=("Segoe UI", 14),
            height=35,
            command=self.create_clip
        )
        self.clip_button.pack(pady=15)

    def paste_url(self):
        """Paste URL from clipboard"""
        try:
            url = self.clipboard_get()
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, url)
            self._on_url_change()
        except:
            pass

    def _on_url_change(self, event=None):
        """Handle URL changes and update preview"""
        url = self.url_entry.get().strip()
        
        # Clear the preview if URL is empty
        if not url:
            self.show_home()
            return
            
        # Only process if URL looks like a YouTube URL
        if 'youtube.com' in url or 'youtu.be' in url:
            self.process_url(url)
        else:
            self.show_error("Please enter a valid YouTube URL")

    def process_url(self, url):
        """Process the YouTube URL and update the preview"""
        try:
            # Basic URL validation
            if not url:
                self.show_home()
                return
                
            # Ensure URL has a scheme
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            # Show loading state
            self.title_label.configure(text="Loading video information...")
            
            def fetch_info():
                try:
                    # Try to get video info
                    video_info = api.get_video_info(url)
                    if video_info:
                        # Transform video info for preview
                        preview_info = {
                            'title': video_info.get('title', 'Unknown Title'),
                            'thumbnail_url': video_info.get('thumbnail', '')
                        }
                        
                        # Update UI in main thread
                        self.after(0, lambda: self.update_preview(preview_info))
                    else:
                        self.after(0, lambda: self.show_error("Could not fetch video information"))
                except Exception as e:
                    logging.error(f"Error processing URL: {e}")
                    self.after(0, lambda: self.show_error("Error loading video"))
            
            # Start fetch in background
            threading.Thread(target=fetch_info, daemon=True).start()
            
        except Exception as e:
            logging.error(f"Error in process_url: {e}")
            self.show_error("Invalid URL format")

    def update_preview(self, video_info):
        """Update the preview with video information"""
        if not video_info:
            self.show_home()
            return

        try:
            # Update thumbnail
            if 'thumbnail_url' in video_info:
                response = requests.get(video_info['thumbnail_url'])
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content))
                    
                    # Resize image for preview
                    img = UIHelper.resize_image(img, (320, 180))
                    
                    # Create CTkImage
                    ctk_img = ctk.CTkImage(light_image=img, dark_image=img, 
                                         size=(320, 180))
                    
                    # Update thumbnail label
                    self.thumbnail_label.configure(image=ctk_img)
                    self.current_thumbnail = ctk_img

            # Update title
            self.title_label.configure(text=video_info.get('title', 'Unknown Title'))
            
            # Show preview frame
            self.home_frame.pack_forget()
            self.preview_frame.pack(fill="both", expand=True, padx=20, pady=15)
            
        except Exception as e:
            logging.error(f"Error updating preview: {str(e)}")
            self.show_error("Error loading video preview")

    def show_error(self, message):
        """Show error message"""
        self.title_label.configure(text=message)
        self.thumbnail_label.configure(image=None)

    def show_home(self):
        """Show the home page"""
        self.preview_frame.pack_forget()
        self.home_frame.pack(fill="both", expand=True)

    def create_clip(self):
        """Create a clip from the video"""
        # This will be implemented later
        pass
