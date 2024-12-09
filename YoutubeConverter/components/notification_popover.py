import os
import sys

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

import customtkinter as ctk
from datetime import datetime
import logging
from components.custom_dropdown import CustomDropdown
from components.tooltip import ModernTooltip

logger = logging.getLogger(__name__)

class NotificationPopover(ctk.CTkToplevel):
    def __init__(self, parent, app):
        logger.info("Initializing NotificationPopover")
        super().__init__(parent)
        
        self.app = app
        self.visible = False
        self._drag_data = {"x": 0, "y": 0, "dragging": False}
        
        # Configure window
        self.title("")
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.configure(fg_color="#1A1A1A")
        
        # Set initial size
        self.geometry("300x400")
        
        # Hide window initially
        self.withdraw()
        logger.debug("Window configured and hidden initially")
        
        # Add shadow effect
        self.shadow_color = "#0A0A0A"
        self.shadow_size = 20
        self.attributes('-transparentcolor', self.shadow_color)
        
        # Create main content
        self.setup_ui()
        
        # Bind events
        self.bind("<Button-1>", self.start_drag)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.stop_drag)
        self.bind("<FocusOut>", self._on_focus_out)
        
        logger.info("NotificationPopover initialization complete")
        
        # Bind global click event to parent
        self.parent = parent
        self.parent.bind("<Button-1>", self.check_click_outside)
        
    def setup_ui(self):
        # Create main frame
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color="#1A1A1A",
            corner_radius=8,
            border_width=1,
            border_color="#333333"
        )
        self.main_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Create header
        self.header = ctk.CTkFrame(
            self.main_frame,
            fg_color="#202020",
            height=45,
            corner_radius=8
        )
        self.header.pack(fill="x", padx=2, pady=(2, 0))
        
        # Header title
        self.title_label = ctk.CTkLabel(
            self.header,
            text="Notifications",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="white"
        )
        self.title_label.pack(side="left", padx=15, pady=10)
        
        # Close button
        self.close_button = ctk.CTkButton(
            self.header,
            text="×",
            width=30,
            height=30,
            corner_radius=15,
            fg_color="transparent",
            hover_color="#303030",
            font=ctk.CTkFont(size=20),
            command=self.hide
        )
        self.close_button.pack(side="right", padx=5, pady=5)
        
        # Create filter controls frame
        self.filter_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.filter_frame.pack(fill="x", padx=10, pady=5)
        
        # Type filter dropdown
        self.type_filter_var = ctk.StringVar(value="all")  
        self.type_filter = CustomDropdown(
            self.filter_frame,
            values=["all", "success", "warning", "error"],
            variable=self.type_filter_var,  
            command=self.update_notifications,
            width=140,
            fg_color="#2D2D2D",
            button_color="#2D2D2D",
            button_hover_color="#383838",
            dropdown_fg_color="#2D2D2D",
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.type_filter.pack(side="left", padx=5, pady=5)
        
        # Sort dropdown
        self.sort_filter_var = ctk.StringVar(value="newest")  
        self.sort_filter = CustomDropdown(
            self.filter_frame,
            values=["newest", "oldest"],
            variable=self.sort_filter_var,  
            command=self.update_notifications,
            width=140,
            fg_color="#2D2D2D",
            button_color="#2D2D2D",
            button_hover_color="#383838",
            dropdown_fg_color="#2D2D2D",
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.sort_filter.pack(side="left", padx=5, pady=5)
        
        # Create scrollable frame for notifications
        self.scrollable = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color="transparent",
            corner_radius=0
        )
        self.scrollable.pack(fill="both", expand=True, padx=2, pady=(0, 2))
        
        # Header buttons frame
        self.buttons_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        self.buttons_frame.pack(side="right", padx=5)
        
        # Mark All button
        self.mark_all_button = ctk.CTkButton(
            self.buttons_frame,
            text="Mark All",
            width=70,
            height=28,
            fg_color="#2D2D2D",
            hover_color="#383838",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            corner_radius=4,
            command=self.mark_all_as_read
        )
        self.mark_all_button.pack(side="left", padx=5)
        
        # Clear All button
        self.clear_button = ctk.CTkButton(
            self.buttons_frame,
            text="Clear All",
            width=70,
            height=28,
            fg_color="#2D2D2D",
            hover_color="#383838",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            corner_radius=4,
            command=self.clear_all
        )
        self.clear_button.pack(side="left", padx=5)
        
    def show(self):
        """Show the notification popover"""
        logger.info("NotificationPopover.show() called")
        if not self.visible:
            logger.info("Setting popover to visible")
            self.visible = True
            self.deiconify()
            self.lift()
            self.attributes('-topmost', True)  # Ensure popover stays on top
            self.focus_force()  # Force focus to the popover
            self.update_notifications()
            logger.info("Popover shown and notifications updated")
        else:
            logger.info("Popover already visible, skipping show()")
            
    def hide(self):
        """Hide the notification popover"""
        logger.info("NotificationPopover.hide() called")
        if self.visible:
            logger.info("Setting popover to hidden")
            self.withdraw()
            self.visible = False
            self.attributes('-topmost', False)  # Remove topmost attribute
            logger.info("Popover hidden")
        else:
            logger.info("Popover already hidden, skipping hide()")
            
    def is_click_inside(self, x_root, y_root):
        """Check if click coordinates are inside the popover window"""
        if not self.visible:
            return False
            
        # Get window geometry
        x = self.winfo_x()
        y = self.winfo_y()
        width = self.winfo_width()
        height = self.winfo_height()
        
        # Check if click is inside window bounds
        inside = (x <= x_root <= x + width and y <= y_root <= y + height)
        logger.debug(f"Click at ({x_root}, {y_root}) is {'inside' if inside else 'outside'} popover")
        return inside
                
    def start_drag(self, event):
        # Don't start drag if clicking on a button, dropdown, or scrollbar
        if isinstance(event.widget, (ctk.CTkButton, CustomDropdown)) or \
           isinstance(event.widget.master, (ctk.CTkButton, CustomDropdown)) or \
           str(event.widget).endswith('scrollbar'):
            return
            
        self._drag_data["x"] = event.x_root - self.winfo_x()
        self._drag_data["y"] = event.y_root - self.winfo_y()
        self._drag_data["dragging"] = True
    
    def on_drag(self, event):
        if self._drag_data["dragging"]:
            x = event.x_root - self._drag_data["x"]
            y = event.y_root - self._drag_data["y"]
            self.geometry(f"+{x}+{y}")
    
    def stop_drag(self, event):
        self._drag_data["dragging"] = False
    
    def _on_focus_out(self, event):
        """Handle focus out event"""
        logger.debug("Focus out event received")
        if not self._drag_data["dragging"]:
            # Only hide if we're not dragging
            self.after(100, self._check_focus)
            
    def _check_focus(self):
        """Check focus after a delay to avoid race conditions"""
        if not self.focus_get():
            logger.info("No focus, hiding popover")
            self.hide()
    
    def on_focus_out(self, event):
        if not self._drag_data["dragging"]:
            self.hide()
    
    def clear_all(self):
        self.app.notifications.clear()
        self.app._save_notifications()
        self.app.update_notification_button()
        self.update_notifications()
    
    def mark_all_as_read(self):
        for notification in self.app.notifications:
            notification["read"] = True
        self.app.update_notification_button()
        self.app._save_notifications()
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string to datetime, handling multiple formats"""
        formats = [
            "%Y-%m-%d %H:%M:%S",  # New format
            "%H:%M",              # Old format
        ]
        
        # Try each format
        for fmt in formats:
            try:
                if fmt == "%H:%M":
                    # For old format, add today's date
                    today = datetime.now().strftime("%Y-%m-%d")
                    return datetime.strptime(f"{today} {timestamp_str}", "%Y-%m-%d %H:%M")
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        # If all formats fail, return a default datetime
        return datetime.now()

    def update_notifications(self, *args):
        # Clear current notifications
        for widget in self.scrollable.winfo_children():
            widget.destroy()
        
        if not self.app.notifications:
            self.empty_label = ctk.CTkLabel(
                self.scrollable,
                text="No notifications",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color="#666666"
            )
            self.empty_label.pack(pady=20)
            return
        
        # Filter notifications
        filtered_notifications = self.app.notifications.copy()
        if self.type_filter_var.get() != "all":
            filtered_notifications = [n for n in filtered_notifications if n["level"] == self.type_filter_var.get()]
        
        # Sort notifications using the new parse function
        reverse_sort = self.sort_filter_var.get() == "newest"
        filtered_notifications.sort(
            key=lambda x: self._parse_timestamp(x["timestamp"]),
            reverse=reverse_sort
        )
        
        # Add notifications
        for notification in filtered_notifications:
            self.add_notification_item(notification)

    def add_notification_item(self, notification):
        # Create frame
        frame = ctk.CTkFrame(
            self.scrollable,
            fg_color="#202020",
            corner_radius=6,
            height=60,
            border_width=1,
            border_color="#333333"
        )
        frame.pack(fill="x", padx=5, pady=3)
        frame.pack_propagate(False)
        
        # Status icon frame with background color
        icon_frame = ctk.CTkFrame(
            frame,
            width=30,
            height=30,
            fg_color=self._get_status_color(notification["level"]),
            corner_radius=4
        )
        icon_frame.pack(side="left", padx=(10, 5), pady=10)
        icon_frame.pack_propagate(False)
        
        # Add icon based on level
        icon = "✓" if notification["level"] == "success" else "⚠️" if notification["level"] == "warning" else "❌"
        icon_label = ctk.CTkLabel(
            icon_frame,
            text=icon,
            font=ctk.CTkFont(size=16),
            text_color="#ffffff"
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Content frame
        content_frame = ctk.CTkFrame(frame, fg_color="transparent")
        content_frame.pack(side="left", fill="both", expand=True, padx=(5, 10), pady=5)
        
        # Add message
        message_label = ctk.CTkLabel(
            content_frame,
            text=notification["message"],
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#ffffff",
            wraplength=200,
            justify="left"
        )
        message_label.pack(side="top", anchor="w", pady=(5, 0))
        
        # Format timestamp for display
        timestamp = self._parse_timestamp(notification["timestamp"])
        display_time = timestamp.strftime("%I:%M %p")  # Format as 12-hour time with AM/PM
        
        time_label = ctk.CTkLabel(
            content_frame,
            text=display_time,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#666666"
        )
        time_label.pack(side="top", anchor="w", pady=(2, 5))
        
        # Extract title from notification message
        # Example message: "Download complete: Video Title"
        title = notification["message"].split(": ", 1)[1] if ": " in notification["message"] else ""
        
        # Make the entire frame clickable to open downloads
        def on_notification_click(event):
            self.hide()  # Hide the notification popover
            # Pass the title to open_downloads to highlight the specific download
            self.app.after(100, lambda: self.app.open_downloads(highlight_title=title))
            
        def on_enter(event):
            frame.configure(fg_color="#252525")  # Slightly lighter on hover
            
        def on_leave(event):
            frame.configure(fg_color="#202020")  # Back to original color
        
        # Bind click event to all widgets
        for widget in [frame, icon_frame, icon_label, content_frame, message_label, time_label]:
            widget.bind("<Button-1>", on_notification_click)
            
        # Bind hover effect to main frame
        frame.bind("<Enter>", on_enter)
        frame.bind("<Leave>", on_leave)
        
        # Add tooltip
        ModernTooltip(frame, text="Click to view in Downloads")

    def _get_status_color(self, level):
        colors = {
            "success": "#2E7D32",  # Dark green
            "warning": "#F57C00",  # Dark orange
            "error": "#C62828"     # Dark red
        }
        return colors.get(level, "#333333")

    def show_notification(self, message, level="info", duration=3000, action=None, title=None):
        """Show a notification with optional action"""
        try:
            # Create notification frame
            notification = self.create_notification(message, level, action, title)
            
            # Add to active notifications
            self.active_notifications.append(notification)
            
            # Show notification
            self.update_notifications()
            
            # Schedule auto-hide
            if duration > 0:
                self.after(duration, lambda: self.hide_notification(notification))
                
        except Exception as e:
            logger.error(f"Error showing notification: {e}")

    def check_click_outside(self, event):
        if not self.is_click_inside(event.x_root, event.y_root):
            self.hide()
