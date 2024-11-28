import customtkinter as ctk
from PIL import Image, ImageTk
import logging
from utils.widget_manager import manager as widget_manager
import urllib.request
from io import BytesIO
from datetime import timedelta
import humanize

# Colors
DARKER_COLOR = "#1a1a1a"
ACCENT_COLOR = "#3d3d3d"
HOVER_COLOR = "#4d4d4d"
TEXT_COLOR = "#ffffff"
BG_COLOR = "#2d2d2d"
DISABLED_COLOR = "#cccccc"

class PreviewCard:
    _image_references = {}

    def __init__(self, parent_container):
        self.create_preview_card(parent_container)

    def create_preview_card(self, parent_container):
        # Preview Container
        self.preview_container = ctk.CTkFrame(parent_container, fg_color=BG_COLOR, corner_radius=15)
        self.preview_container.pack(fill="x", pady=(0, 20))

        # Preview Frame (Left side)
        self.preview_frame = ctk.CTkFrame(self.preview_container, fg_color=BG_COLOR, height=200, corner_radius=12)
        self.preview_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.preview_frame.pack_propagate(False)

        # Video Info Frame (Right side)
        self.video_info_frame = ctk.CTkFrame(self.preview_container, fg_color=BG_COLOR, width=300, corner_radius=12)
        self.video_info_frame.pack(side="right", fill="y", padx=10, pady=10)
        self.video_info_frame.pack_propagate(False)

        # Default preview text
        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="Video preview will appear here",
            font=ctk.CTkFont(size=14),
            text_color=DISABLED_COLOR
        )
        self.preview_label.pack(expand=True)

    def update_preview(self, video_info):
        """Update the preview with video information"""
        # Clear existing widgets
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        for widget in self.video_info_frame.winfo_children():
            widget.destroy()

        try:
            # Load and display thumbnail
            response = urllib.request.urlopen(video_info['thumbnail_url'])
            image_data = response.read()
            image = Image.open(BytesIO(image_data))
            
            # Calculate new dimensions maintaining aspect ratio
            target_width = 400
            aspect_ratio = image.width / image.height
            new_width = target_width
            new_height = int(target_width / aspect_ratio)
            
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # Store reference to prevent garbage collection
            preview_key = str(self.preview_frame)
            PreviewCard._image_references[preview_key] = {
                'image': image,
                'photo': photo
            }
            
            preview_label = widget_manager.create_managed_widget(
                ctk.CTkLabel,
                self.preview_frame,
                image=photo,
                text=""
            )
            preview_label.image = photo  # Keep a reference at widget level too
            preview_label.pack(expand=True)

            # Bind cleanup to widget destruction
            def cleanup_image(widget=preview_label, key=preview_key):
                if key in PreviewCard._image_references:
                    del PreviewCard._image_references[key]
            preview_label.bind("<Destroy>", lambda e: cleanup_image())

        except Exception as thumb_error:
            logging.error(f"Error loading thumbnail: {thumb_error}")
            error_label = widget_manager.create_managed_widget(
                ctk.CTkLabel,
                self.preview_frame,
                text="Thumbnail unavailable",
                font=ctk.CTkFont(size=14),
                text_color=DISABLED_COLOR
            )
            error_label.pack(expand=True)

        # Add video information using managed widgets
        info_container = widget_manager.create_managed_widget(
            ctk.CTkFrame,
            self.video_info_frame,
            fg_color="#2d2d2d",
            corner_radius=15
        )
        info_container.pack(fill="both", expand=True, padx=10, pady=10)

        title_label = widget_manager.create_managed_widget(
            ctk.CTkLabel,
            info_container,
            text=video_info['title'],
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT_COLOR,
            wraplength=260,
            justify="left"
        )
        title_label.pack(pady=(15, 5), padx=15, anchor="w")

        # Channel info with icon
        channel_frame = widget_manager.create_managed_widget(
            ctk.CTkFrame,
            info_container,
            fg_color="transparent",
            height=25
        )
        channel_frame.pack(fill="x", padx=15, pady=(0, 10), anchor="w")

        channel_icon = widget_manager.create_managed_widget(
            ctk.CTkLabel,
            channel_frame,
            text="👤",
            font=ctk.CTkFont(size=14),
            text_color="#888888"
        )
        channel_icon.pack(side="left", padx=(0, 5))

        channel_label = widget_manager.create_managed_widget(
            ctk.CTkLabel,
            channel_frame,
            text=video_info['author'],
            font=ctk.CTkFont(size=13),
            text_color="#888888"
        )
        channel_label.pack(side="left")

        # Stats container
        stats_frame = widget_manager.create_managed_widget(
            ctk.CTkFrame,
            info_container,
            fg_color="#232323",
            corner_radius=12,
            height=80
        )
        stats_frame.pack(fill="x", padx=15, pady=(0, 15))
        stats_frame.pack_propagate(False)

        # Stats grid
        grid_frame = widget_manager.create_managed_widget(
            ctk.CTkFrame,
            stats_frame,
            fg_color="transparent"
        )
        grid_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Duration with icon
        duration_frame = widget_manager.create_managed_widget(
            ctk.CTkFrame,
            grid_frame,
            fg_color="transparent"
        )
        duration_frame.pack(pady=2)

        duration_icon = widget_manager.create_managed_widget(
            ctk.CTkLabel,
            duration_frame,
            text="⏱️",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        duration_icon.pack(side="left", padx=(0, 5))

        duration_label = widget_manager.create_managed_widget(
            ctk.CTkLabel,
            duration_frame,
            text=str(timedelta(seconds=video_info['length'])) if video_info.get('length') else "Duration unavailable",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        duration_label.pack(side="left")

        # Views with icon
        views_frame = widget_manager.create_managed_widget(
            ctk.CTkFrame,
            grid_frame,
            fg_color="transparent"
        )
        views_frame.pack(pady=2)

        views_icon = widget_manager.create_managed_widget(
            ctk.CTkLabel,
            views_frame,
            text="👁️",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        views_icon.pack(side="left", padx=(0, 5))

        views_label = widget_manager.create_managed_widget(
            ctk.CTkLabel,
            views_frame,
            text=humanize.intword(video_info['views']) if video_info.get('views') else "Views unavailable",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        views_label.pack(side="left")

        # Publish date with icon
        if video_info.get('published'):
            date_frame = widget_manager.create_managed_widget(
                ctk.CTkFrame,
                grid_frame,
                fg_color="transparent"
            )
            date_frame.pack(pady=2)

            date_icon = widget_manager.create_managed_widget(
                ctk.CTkLabel,
                date_frame,
                text="📅",
                font=ctk.CTkFont(size=12),
                text_color="#888888"
            )
            date_icon.pack(side="left", padx=(0, 5))

            date_label = widget_manager.create_managed_widget(
                ctk.CTkLabel,
                date_frame,
                text=video_info['published'],
                font=ctk.CTkFont(size=12),
                text_color="#888888"
            )
            date_label.pack(side="left")
