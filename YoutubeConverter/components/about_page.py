import customtkinter as ctk
import threading
import time

DARKER_COLOR = "#1a1a1a"
ACCENT_COLOR = "#333333"
HOVER_COLOR = "#404040"
TEXT_COLOR = "#ffffff"

class AboutPage(ctk.CTkFrame):
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
            text="About",
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
        
        # Add about content
        self.add_about_sections()

    def handle_back_click(self):
        """Handle back button click"""
        if self.on_back_click:
            # Disable buttons during animation
            self.back_button.configure(state="disabled")
            self.close_button.configure(state="disabled")
            # Call the callback
            self.on_back_click()

    def add_section_title(self, text):
        """Add a section title to the about page"""
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

    def add_about_sections(self):
        """Add about content sections"""
        # Overview Section
        self.add_section_title("Overview")
        overview_frame = ctk.CTkFrame(self.content, fg_color="#232323", corner_radius=8)
        overview_frame.pack(fill="x", pady=5)
        
        overview_text = """YouTube Converter is a modern, user-friendly application that allows you to easily download YouTube videos with a beautiful and intuitive interface."""
        
        overview_label = ctk.CTkLabel(
            overview_frame,
            text=overview_text,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color="#ffffff",
            wraplength=500,
            justify="left"
        )
        overview_label.pack(padx=15, pady=15)

        # Features Section
        self.add_section_title("Features")
        features_frame = ctk.CTkFrame(self.content, fg_color="#232323", corner_radius=8)
        features_frame.pack(fill="x", pady=5)
        
        features = [
            "• Simple and intuitive interface",
            "• High-quality video downloads",
            "• Multiple format options",
            "• Custom download settings",
            "• Beautiful animations and transitions"
        ]
        
        features_label = ctk.CTkLabel(
            features_frame,
            text="\n".join(features),
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color="#ffffff",
            justify="left"
        )
        features_label.pack(padx=15, pady=15, anchor="w")

        # Version Info Section
        self.add_section_title("Version Information")
        version_frame = ctk.CTkFrame(self.content, fg_color="#232323", corner_radius=8)
        version_frame.pack(fill="x", pady=5)
        
        version_text = """Version: 1.0.0\nCreated with ❤️ using Python and CustomTkinter"""
        
        version_label = ctk.CTkLabel(
            version_frame,
            text=version_text,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color="#ffffff",
            justify="left"
        )
        version_label.pack(padx=15, pady=15)

    @staticmethod
    def open(parent_frame, on_back_click):
        """Open the about page"""
        for widget in parent_frame.winfo_children():
            widget.destroy()
        about_frame = AboutPage(parent_frame, on_back_click=on_back_click)
        about_frame.pack(fill="both", expand=True)
        return about_frame
