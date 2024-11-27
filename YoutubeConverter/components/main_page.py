import customtkinter as ctk
from components.buttons import AnimatedButton

# Colors
DARKER_COLOR = "#1a1a1a"
ACCENT_COLOR = "#3d3d3d"
HOVER_COLOR = "#4d4d4d"
TEXT_COLOR = "#ffffff"
BG_COLOR = "#2d2d2d"
DISABLED_COLOR = "#cccccc"

class MainPage:
    @staticmethod
    def open(parent_frame):
        """Create and show the main page"""
        # URL Entry Frame
        url_frame = ctk.CTkFrame(parent_frame, fg_color=DARKER_COLOR)
        url_frame.pack(fill="x", padx=20, pady=(0, 20))

        # URL Entry
        url_entry = ctk.CTkEntry(
            url_frame,
            placeholder_text="Enter YouTube URL",
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=BG_COLOR,
            border_color=ACCENT_COLOR,
            text_color=TEXT_COLOR
        )
        url_entry.pack(side="left", fill="x", expand=True)

        # Download Button
        download_button = AnimatedButton(
            url_frame,
            text="Download",
            command=lambda: MainPage.start_download(url_entry, status_label, progress_bar),
            width=120,
            height=40,
            fg_color=ACCENT_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR,
            tooltip_text="Start downloading"
        )
        download_button.pack(side="right", padx=(10, 0))

        # Progress Frame
        progress_frame = ctk.CTkFrame(parent_frame, fg_color=DARKER_COLOR)
        progress_frame.pack(fill="x", padx=20, pady=20)

        # Progress Bar
        progress_bar = ctk.CTkProgressBar(
            progress_frame,
            mode="determinate",
            height=15,
            corner_radius=10,
            fg_color=BG_COLOR,
            progress_color=ACCENT_COLOR
        )
        progress_bar.pack(fill="x", padx=20, pady=(20, 10))
        progress_bar.set(0)

        # Status Label
        status_label = ctk.CTkLabel(
            progress_frame,
            text="Ready to download",
            font=ctk.CTkFont(size=12),
            text_color=DISABLED_COLOR
        )
        status_label.pack(pady=(0, 20))

    @staticmethod
    def start_download(url_entry, status_label, progress_bar):
        """Start the download process"""
        url = url_entry.get()
        if not url:
            status_label.configure(text="Please enter a YouTube URL")
            return
            
        status_label.configure(text="Download started...")
        progress_bar.set(0)
        # TODO: Implement actual download functionality
