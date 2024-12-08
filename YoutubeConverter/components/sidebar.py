import customtkinter as ctk
import threading
import time
from utils.ui_helper import UIHelper

class SmoothSidebar(ctk.CTkFrame):
    def __init__(self, master, width=250, **kwargs):
        # Set width in the constructor and add corner radius
        kwargs["width"] = width
        kwargs["corner_radius"] = 12
        kwargs["border_width"] = 2  # Increased border width
        kwargs["border_color"] = "#404040"  # Lighter border color
        super().__init__(master, **kwargs)

        self.width = width
        self.visible = False
        self.animating = False

        # Configure the sidebar with a darker theme
        self.configure(fg_color="#1a1a1a")  # Darker background

        # Create a container for content
        self.content_frame = UIHelper.create_section_frame(
            self,
            height=0,  # Let it expand
            fg_color="transparent",
            corner_radius=0
        )
        self.content_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Menu title with modern styling
        title_frame = UIHelper.create_section_frame(
            self.content_frame,
            height=50,
            fg_color="transparent",
            corner_radius=0
        )
        title_frame.pack(fill="x", pady=(10, 5))

        # Create title text container with improved font
        UIHelper.create_text_container(
            title_frame,
            title="MENU",
            description="",
            title_font=("Arial", 24, "bold"),
            title_color="#FFFFFF"
        ).pack(side="left", padx=(5, 0))

        # Add white separator line with increased visibility
        separator = UIHelper.create_section_frame(
            self.content_frame,
            height=1,  # Reduced to 1px
            fg_color="#FFFFFF",
            corner_radius=0
        )
        separator.pack(fill="x", pady=(5, 15))

        # Modern separator with gradient effect
        separator_frame = UIHelper.create_section_frame(
            self.content_frame,
            height=2,
            fg_color="transparent",
            corner_radius=0
        )
        separator_frame.pack(fill="x", pady=(0, 25))

        # Create two separators for gradient effect
        sep1 = UIHelper.create_section_frame(
            separator_frame,
            height=1,
            fg_color="#404040",
            corner_radius=0
        )
        sep1.pack(fill="x")
        sep2 = UIHelper.create_section_frame(
            separator_frame,
            height=1,
            fg_color="#0d0d0d",
            corner_radius=0
        )
        sep2.pack(fill="x")

        # Initially place the sidebar off-screen with a small offset
        self.place(relx=1.0, rely=0, relheight=1, x=2)

        # Bind click events
        self.master.bind("<Button-1>", self.check_click_outside)
        self.bind("<Button-1>", self.on_sidebar_click)

    def add_menu_item(self, icon, text, command=None):
        """Add a styled menu item to the sidebar"""
        # Create frame for better layout control
        frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        frame.pack(fill="x", pady=4)

        # Create icon label
        icon_label = ctk.CTkLabel(
            frame,
            text=icon,
            font=ctk.CTkFont(family="Segoe UI", size=16),
            text_color="#ffffff",
            width=25
        )
        icon_label.pack(side="left", padx=(10, 5))

        # Create button
        button = ctk.CTkButton(
            frame,
            text=text,
            command=command,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            fg_color="transparent",
            hover_color="#2d2d2d",
            text_color="#ffffff",
            anchor="w",
            height=40,
            corner_radius=8
        )
        button.pack(fill="x", padx=(0, 10))
        return button

    def on_sidebar_click(self, event):
        """Handle clicks on the sidebar"""
        # Prevent click from propagating to master
        return "break"

    def check_click_outside(self, event):
        """Check if click is outside the sidebar"""
        if not self.visible:
            return

        # Get the widget under cursor
        widget_under_cursor = event.widget.winfo_containing(event.x_root, event.y_root)

        # Check if click is outside sidebar
        if widget_under_cursor != self and not self.is_descendant(widget_under_cursor):
            self.toggle()

    def is_descendant(self, widget):
        """Check if a widget is a descendant of the sidebar"""
        if widget is None:
            return False
        while widget.master:
            if widget.master == self:
                return True
            widget = widget.master
        return False

    def toggle(self):
        """Toggle sidebar visibility with animation"""
        if self.animating:
            return

        self.animating = True
        if self.visible:
            self._animate_out()
        else:
            self._animate_in()

    def _animate_in(self):
        """Animate sidebar sliding in"""
        start_x = 2
        target_x = -self.width + 2
        steps = 20
        step_size = (target_x - start_x) / steps

        def animate_step(step):
            if step < steps:
                new_x = start_x + step_size * step
                self.place(relx=1.0, rely=0, relheight=1, x=new_x)
                self.master.after(10, lambda: animate_step(step + 1))
            else:
                self.visible = True
                self.animating = False

        self.lift()  # Bring sidebar to front
        animate_step(0)

    def _animate_out(self):
        """Animate sidebar sliding out"""
        start_x = -self.width + 2
        target_x = 2
        steps = 20
        step_size = (target_x - start_x) / steps

        def animate_step(step):
            if step < steps:
                new_x = start_x + step_size * step
                self.place(relx=1.0, rely=0, relheight=1, x=new_x)
                self.master.after(10, lambda: animate_step(step + 1))
            else:
                self.visible = False
                self.animating = False
                self.place_forget()

        animate_step(0)

    def setup_menu_items(self, app):
        """Set up all menu items with their respective app functions"""
        menu_items = [
            ("⚙️", "Settings", app.open_settings),
            ("📥", "Downloads", app.open_downloads),
            ("🎨", "Themes", app.open_themes),
            ("✂️", "Clipping", app.open_clipping),
            ("📊", "Statistics", app.open_statistics),
            ("ℹ️", "About", app.open_about),
            ("❔", "Help", app.open_help)
        ]

        for icon, text, command in menu_items:
            self.add_menu_item(icon, text, command)

    def hide(self):
        if self.visible:
            self.toggle()
