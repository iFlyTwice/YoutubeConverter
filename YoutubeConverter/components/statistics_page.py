import customtkinter as ctk
import json
import os
from datetime import datetime

DARKER_COLOR = "#1a1a1a"
ACCENT_COLOR = "#333333"
HOVER_COLOR = "#404040"
TEXT_COLOR = "#ffffff"

class StatisticsPage(ctk.CTkFrame):
    def __init__(self, master, app=None, on_back_click=None, **kwargs):
        # Store parameters before super().__init__
        self.app = app
        self.on_back_click = on_back_click
        # Remove app and on_back_click from kwargs
        kwargs.pop('app', None)
        kwargs.pop('on_back_click', None)
        super().__init__(master, **kwargs)
        
        # Configure the frame
        self.configure(fg_color="#1a1a1a", corner_radius=12)
        
        # Create header
        self.header = ctk.CTkFrame(self, fg_color="#232323", height=60, corner_radius=12)
        self.header.pack(fill="x", padx=15, pady=(15, 0))
        self.header.pack_propagate(False)
        
        # Add back button with arrow
        self.back_button = ctk.CTkButton(
            self.header,
            text="←",  # Left arrow
            width=40,
            height=40,
            font=ctk.CTkFont(size=20),
            fg_color="transparent",
            hover_color="#3d3d3d",
            corner_radius=8,
            command=self.handle_back_click
        )
        self.back_button.pack(side="left", padx=10)
        
        # Add title to header
        self.title = ctk.CTkLabel(
            self.header,
            text="Statistics",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#ffffff"
        )
        self.title.pack(side="left", padx=(5, 20))
        
        # Add close button
        self.close_button = ctk.CTkButton(
            self.header,
            text="×",
            width=40,
            height=40,
            font=ctk.CTkFont(size=20),
            fg_color="transparent",
            hover_color="#3d3d3d",
            corner_radius=8,
            command=self.handle_back_click
        )
        self.close_button.pack(side="right", padx=10)
        
        # Create content area with scrollable frame
        self.content = ctk.CTkScrollableFrame(
            self,
            fg_color="#1a1a1a",
            corner_radius=0
        )
        self.content.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Add statistics content
        self.add_statistics_sections()
    
    def add_section_title(self, text):
        """Add a section title to the statistics page"""
        frame = ctk.CTkFrame(self.content, fg_color="transparent", height=50)
        frame.pack(fill="x", pady=(20, 10))
        frame.pack_propagate(False)
        
        label = ctk.CTkLabel(
            frame,
            text=text,
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#ffffff"
        )
        label.pack(side="left")
        
        # Add separator
        separator = ctk.CTkFrame(self.content, fg_color="#333333", height=1)
        separator.pack(fill="x", pady=(0, 10))

    def add_stat_card(self, title, value, description=""):
        """Add a statistics card"""
        frame = ctk.CTkFrame(self.content, fg_color="#232323", height=100, corner_radius=8)
        frame.pack(fill="x", pady=5)
        
        # Title
        title_label = ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#ffffff"
        )
        title_label.pack(padx=15, pady=(15, 5))
        
        # Value
        value_label = ctk.CTkLabel(
            frame,
            text=str(value),
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color="#4CAF50"  # Green color for values
        )
        value_label.pack(pady=5)
        
        # Description
        if description:
            desc_label = ctk.CTkLabel(
                frame,
                text=description,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color="#888888"
            )
            desc_label.pack(padx=15, pady=(0, 15))

    def load_statistics(self):
        """Load statistics from the statistics file"""
        stats_file = os.path.join(os.path.dirname(__file__), "statistics.json")
        try:
            with open(stats_file, "r") as f:
                return json.load(f)
        except:
            return {
                "total_downloads": 0,
                "total_size": 0,
                "formats": {
                    "mp4": 0,
                    "mkv": 0,
                    "webm": 0
                },
                "quality_levels": {
                    "4K": 0,
                    "1080p": 0,
                    "720p": 0,
                    "480p": 0,
                    "360p": 0
                },
                "recent_downloads": []
            }

    def format_size(self, size_bytes):
        """Format size in bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    def add_statistics_sections(self):
        """Add statistics content sections"""
        stats = self.load_statistics()
        
        # Overview Section
        self.add_section_title("Overview")
        self.add_stat_card(
            "Total Downloads",
            stats["total_downloads"],
            "Videos downloaded since installation"
        )
        self.add_stat_card(
            "Total Size",
            self.format_size(stats["total_size"]),
            "Total size of all downloads"
        )
        
        # Format Distribution Section
        self.add_section_title("Format Distribution")
        format_frame = ctk.CTkFrame(self.content, fg_color="#232323", corner_radius=8)
        format_frame.pack(fill="x", pady=5)
        
        for format_name, count in stats["formats"].items():
            format_row = ctk.CTkFrame(format_frame, fg_color="transparent")
            format_row.pack(fill="x", padx=15, pady=5)
            
            name_label = ctk.CTkLabel(
                format_row,
                text=format_name.upper(),
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color="#ffffff"
            )
            name_label.pack(side="left")
            
            count_label = ctk.CTkLabel(
                format_row,
                text=str(count),
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color="#4CAF50"
            )
            count_label.pack(side="right")
        
        # Quality Distribution Section
        self.add_section_title("Quality Distribution")
        quality_frame = ctk.CTkFrame(self.content, fg_color="#232323", corner_radius=8)
        quality_frame.pack(fill="x", pady=5)
        
        for quality, count in stats["quality_levels"].items():
            quality_row = ctk.CTkFrame(quality_frame, fg_color="transparent")
            quality_row.pack(fill="x", padx=15, pady=5)
            
            name_label = ctk.CTkLabel(
                quality_row,
                text=quality,
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color="#ffffff"
            )
            name_label.pack(side="left")
            
            count_label = ctk.CTkLabel(
                quality_row,
                text=str(count),
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color="#4CAF50"
            )
            count_label.pack(side="right")
        
        # Recent Downloads Section
        self.add_section_title("Recent Downloads")
        recent_frame = ctk.CTkFrame(self.content, fg_color="#232323", corner_radius=8)
        recent_frame.pack(fill="x", pady=5)
        
        if not stats["recent_downloads"]:
            no_downloads_label = ctk.CTkLabel(
                recent_frame,
                text="No recent downloads",
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color="#888888"
            )
            no_downloads_label.pack(padx=15, pady=15)
        else:
            for download in stats["recent_downloads"][-5:]:  # Show last 5 downloads
                download_row = ctk.CTkFrame(recent_frame, fg_color="transparent")
                download_row.pack(fill="x", padx=15, pady=5)
                
                title_label = ctk.CTkLabel(
                    download_row,
                    text=download["title"],
                    font=ctk.CTkFont(family="Segoe UI", size=14),
                    text_color="#ffffff"
                )
                title_label.pack(side="left")
                
                date_label = ctk.CTkLabel(
                    download_row,
                    text=datetime.fromtimestamp(download["timestamp"]).strftime("%Y-%m-%d %H:%M"),
                    font=ctk.CTkFont(family="Segoe UI", size=12),
                    text_color="#888888"
                )
                date_label.pack(side="right")

    def handle_back_click(self):
        """Handle back button click"""
        if self.on_back_click:
            # Disable buttons during animation
            self.back_button.configure(state="disabled")
            self.close_button.configure(state="disabled")
            # Call the callback
            self.on_back_click()

    @staticmethod
    def open(parent_frame, on_back_click):
        """Open the statistics page"""
        for widget in parent_frame.winfo_children():
            widget.destroy()
        statistics_frame = StatisticsPage(parent_frame, on_back_click=on_back_click)
        statistics_frame.pack(fill="both", expand=True)
        return statistics_frame
