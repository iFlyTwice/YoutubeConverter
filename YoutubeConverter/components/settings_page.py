import customtkinter as ctk
import threading
import time

DARKER_COLOR = "#1a1a1a"
ACCENT_COLOR = "#333333"
HOVER_COLOR = "#404040"
TEXT_COLOR = "#ffffff"

class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, on_back_click=None, **kwargs):
        super().__init__(master, **kwargs)
        
        # Store callback
        self.on_back_click = on_back_click
        
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
            text="Settings",
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
        
        # Add settings sections
        self.add_settings_sections()

    def handle_back_click(self):
        """Handle back button click"""
        if self.on_back_click:
            # Disable buttons during animation
            self.back_button.configure(state="disabled")
            self.close_button.configure(state="disabled")
            # Call the callback
            self.on_back_click()

    def add_settings_sections(self):
        # Download Settings Section
        self.add_section_title("Download Settings")
        
        # Output Directory
        self.add_setting_item(
            "Output Directory",
            "Choose where to save downloaded videos",
            "folder"
        )
        
        # Video Quality
        self.add_setting_item(
            "Video Quality",
            "Select preferred video quality",
            "dropdown",
            options=["Highest", "1080p", "720p", "480p", "360p"]
        )
        
        # Audio Settings Section
        self.add_section_title("Audio Settings")
        
        # Audio Format
        self.add_setting_item(
            "Audio Format",
            "Choose audio format for extraction",
            "dropdown",
            options=["MP3", "WAV", "AAC", "M4A"]
        )
        
        # Audio Quality
        self.add_setting_item(
            "Audio Quality",
            "Select audio bitrate",
            "dropdown",
            options=["320kbps", "256kbps", "192kbps", "128kbps"]
        )
        
        # Appearance Section
        self.add_section_title("Appearance")
        
        # Theme
        self.add_setting_item(
            "Theme",
            "Choose application theme",
            "dropdown",
            options=["Dark", "Light", "System"]
        )
        
    def add_section_title(self, text):
        """Add a section title to the settings"""
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
        
    def add_setting_item(self, title, description, type_, **kwargs):
        """Add a setting item with title, description and appropriate control"""
        frame = ctk.CTkFrame(self.content, fg_color="#232323", height=70, corner_radius=8)
        frame.pack(fill="x", pady=5)
        frame.pack_propagate(False)
        
        # Text container
        text_frame = ctk.CTkFrame(frame, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            text_frame,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#ffffff"
        )
        title_label.pack(anchor="w")
        
        # Description
        desc_label = ctk.CTkLabel(
            text_frame,
            text=description,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#888888"
        )
        desc_label.pack(anchor="w")
        
        # Control
        if type_ == "dropdown":
            control = ctk.CTkOptionMenu(
                frame,
                values=kwargs.get("options", []),
                fg_color="#333333",
                button_color="#404040",
                button_hover_color="#4d4d4d",
                width=120
            )
            control.pack(side="right", padx=15)
        elif type_ == "folder":
            control = ctk.CTkButton(
                frame,
                text="Browse",
                fg_color="#333333",
                hover_color="#404040",
                width=100
            )
            control.pack(side="right", padx=15)
            
    @staticmethod
    def open(parent_frame, on_back_click):
        """Open the settings page"""
        for widget in parent_frame.winfo_children():
            widget.destroy()
        settings_frame = SettingsPage(parent_frame, on_back_click=on_back_click)
        settings_frame.pack(fill="both", expand=True)
        return settings_frame
