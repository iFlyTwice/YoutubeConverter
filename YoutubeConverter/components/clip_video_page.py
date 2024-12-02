import customtkinter as ctk
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class ClipVideoPage:
    """
    A page for clipping downloaded videos to specific time ranges.
    """
    
    @classmethod
    def open(cls, container):
        """
        Creates and displays the clip video page in the given container.
        
        Args:
            container: The parent container to place the page in
        """
        return cls(container)
    
    def __init__(self, container):
        self.container = container
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface for the clip video page"""
        # Clear existing widgets in container
        for widget in self.container.winfo_children():
            widget.destroy()
            
        # Main frame
        self.main_frame = ctk.CTkFrame(self.container, fg_color="#1a1a1a")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            self.main_frame,
            text="Video Clipper",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Video selection frame
        self.video_frame = ctk.CTkFrame(self.main_frame, fg_color="#2b2b2b")
        self.video_frame.pack(fill="x", padx=20, pady=10)
        
        # Video selection dropdown
        self.video_var = ctk.StringVar(value="Select a video")
        self.video_dropdown = ctk.CTkOptionMenu(
            self.video_frame,
            variable=self.video_var,
            values=["No videos available"],
            command=self.on_video_select,
            width=300
        )
        self.video_dropdown.pack(pady=10)
        
        # Time range frame
        time_frame = ctk.CTkFrame(self.main_frame, fg_color="#2b2b2b")
        time_frame.pack(fill="x", padx=20, pady=10)
        
        # Start time entry
        start_frame = ctk.CTkFrame(time_frame, fg_color="#2b2b2b")
        start_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(start_frame, text="Start Time (HH:MM:SS):").pack(side="left", padx=5)
        self.start_time = ctk.CTkEntry(start_frame, placeholder_text="00:00:00")
        self.start_time.pack(side="left", padx=5)
        
        # End time entry
        end_frame = ctk.CTkFrame(time_frame, fg_color="#2b2b2b")
        end_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(end_frame, text="End Time (HH:MM:SS):  ").pack(side="left", padx=5)
        self.end_time = ctk.CTkEntry(end_frame, placeholder_text="00:00:00")
        self.end_time.pack(side="left", padx=5)
        
        # Clip button
        self.clip_button = ctk.CTkButton(
            self.main_frame,
            text="Create Clip",
            command=self.create_clip,
            state="disabled"
        )
        self.clip_button.pack(pady=20)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            wraplength=400
        )
        self.status_label.pack(pady=10)
        
        # Try to load available videos
        self.load_available_videos()
        
    def load_available_videos(self):
        """Load the list of available downloaded videos"""
        # TODO: Implement loading videos from downloads directory
        logger.info("Loading available videos")
        # For now, we'll just show a placeholder
        self.video_dropdown.configure(values=["No videos available"])
        
    def on_video_select(self, choice):
        """Handle video selection from dropdown"""
        if choice != "No videos available":
            self.clip_button.configure(state="normal")
        else:
            self.clip_button.configure(state="disabled")
            
    def validate_time_format(self, time_str):
        """Validate time format (HH:MM:SS)"""
        try:
            hours, minutes, seconds = map(int, time_str.split(':'))
            if not (0 <= hours <= 99 and 0 <= minutes <= 59 and 0 <= seconds <= 59):
                return False
            return True
        except ValueError:
            return False
            
    def create_clip(self):
        """Create a video clip using the specified time range"""
        start = self.start_time.get()
        end = self.end_time.get()
        
        # Validate time formats
        if not self.validate_time_format(start) or not self.validate_time_format(end):
            self.status_label.configure(
                text="Invalid time format. Please use HH:MM:SS",
                text_color="red"
            )
            return
            
        # TODO: Implement video clipping functionality
        logger.info(f"Creating clip from {start} to {end}")
        self.status_label.configure(
            text="Video clipping will be implemented in a future update.",
            text_color="white"
        )
