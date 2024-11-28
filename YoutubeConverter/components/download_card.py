import customtkinter as ctk
from typing import Optional, Callable
import threading
import humanize

class DownloadCard(ctk.CTkFrame):
    def __init__(self, master, title: str, thumbnail: Optional[str] = None,
                 on_cancel: Optional[Callable] = None, **kwargs):
        super().__init__(master, fg_color="#232323", corner_radius=8, **kwargs)

        # Store callback
        self.on_cancel = on_cancel
        self._is_cancelled = False

        # Main container
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=15, pady=10)

        # Title
        self.title_label = ctk.CTkLabel(
            self.container,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#ffffff"
        )
        self.title_label.pack(anchor="w")

        # Progress frame
        self.progress_frame = ctk.CTkFrame(self.container, fg_color="transparent", height=30)
        self.progress_frame.pack(fill="x", pady=(10, 0))
        self.progress_frame.pack_propagate(False)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            mode="determinate",
            progress_color="#4CAF50",
            fg_color="#333333",
            height=6
        )
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.progress_bar.set(0)

        # Status label
        self.status_label = ctk.CTkLabel(
            self.container,
            text="Starting download...",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#888888"
        )
        self.status_label.pack(anchor="w", pady=(5, 0))

        # Cancel button
        if on_cancel:
            self.cancel_button = ctk.CTkButton(
                self.progress_frame,
                text="×",
                width=30,
                height=30,
                fg_color="#333333",
                hover_color="#404040",
                command=self._handle_cancel
            )
            self.cancel_button.pack(side="right")

    def update_progress(self, progress: float, status: Optional[str] = None):
        """Update download progress"""
        def update():
            self.progress_bar.set(progress / 100)
            if status:
                self.status_label.configure(text=status)

        if self.winfo_exists():
            self.after(0, update)

    def _handle_cancel(self):
        """Handle cancel button click"""
        self._is_cancelled = True
        if self.on_cancel:
            self.on_cancel()

    @property
    def is_cancelled(self) -> bool:
        return self._is_cancelled
