import customtkinter as ctk
import threading
import time

DARKER_COLOR = "#1a1a1a"
ACCENT_COLOR = "#333333"
HOVER_COLOR = "#404040"
TEXT_COLOR = "#ffffff"

class HelpPage(ctk.CTkFrame):
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
            text="Help",
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
        
        # Add help content
        self.add_help_sections()

    def handle_back_click(self):
        """Handle back button click"""
        if self.on_back_click:
            # Disable buttons during animation
            self.back_button.configure(state="disabled")
            self.close_button.configure(state="disabled")
            # Call the callback
            self.on_back_click()

    def add_section_title(self, text):
        """Add a section title to the help page"""
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

    def add_help_sections(self):
        """Add help content sections"""
        # Getting Started Section
        self.add_section_title("Getting Started")
        getting_started_frame = ctk.CTkFrame(self.content, fg_color="#232323", corner_radius=8)
        getting_started_frame.pack(fill="x", pady=5)
        
        getting_started_text = """1. Paste a YouTube URL in the input field
2. Click the Download button
3. Choose your preferred quality settings
4. Wait for the download to complete"""
        
        getting_started_label = ctk.CTkLabel(
            getting_started_frame,
            text=getting_started_text,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color="#ffffff",
            justify="left"
        )
        getting_started_label.pack(padx=15, pady=15, anchor="w")

        # FAQ Section
        self.add_section_title("Frequently Asked Questions")
        faq_frame = ctk.CTkFrame(self.content, fg_color="#232323", corner_radius=8)
        faq_frame.pack(fill="x", pady=5)
        
        faq_text = """Q: What video formats are supported?
A: We support MP4, MKV, and WebM formats.

Q: What audio formats can I extract?
A: You can extract audio in MP3, WAV, AAC, and M4A formats.

Q: Where are my downloads saved?
A: By default, files are saved to your Downloads folder. You can change this in Settings.

Q: What's the maximum quality available?
A: You can download videos up to their original quality, including 4K if available."""
        
        faq_label = ctk.CTkLabel(
            faq_frame,
            text=faq_text,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color="#ffffff",
            justify="left"
        )
        faq_label.pack(padx=15, pady=15, anchor="w")

        # Troubleshooting Section
        self.add_section_title("Troubleshooting")
        troubleshooting_frame = ctk.CTkFrame(self.content, fg_color="#232323", corner_radius=8)
        troubleshooting_frame.pack(fill="x", pady=5)
        
        troubleshooting_text = """• If download fails, check your internet connection
• Ensure the YouTube URL is valid and the video is available
• Try selecting a lower quality if download is slow
• Clear your temporary files if you encounter errors
• Make sure you have enough disk space"""
        
        troubleshooting_label = ctk.CTkLabel(
            troubleshooting_frame,
            text=troubleshooting_text,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color="#ffffff",
            justify="left"
        )
        troubleshooting_label.pack(padx=15, pady=15, anchor="w")

    @staticmethod
    def open(parent_frame, on_back_click):
        """Open the help page"""
        for widget in parent_frame.winfo_children():
            widget.destroy()
        help_frame = HelpPage(parent_frame, on_back_click=on_back_click)
        help_frame.pack(fill="both", expand=True)
        return help_frame
