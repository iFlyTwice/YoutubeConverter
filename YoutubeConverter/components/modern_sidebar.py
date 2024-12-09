import customtkinter as ctk
import logging
from utils.ui_helper import UIHelper

logger = logging.getLogger(__name__)

class ModernSidebar(ctk.CTkFrame):
    def __init__(self, master, width=UIHelper.MENU_WIDTH, **kwargs):
        super().__init__(
            master,
            width=width,
            height=master.winfo_height(),
            corner_radius=0,
            border_width=0,
            **kwargs
        )
        
        self.master = master
        self.width = width
        self.visible = False
        self.animating = False
        
        # Create overlay
        self.overlay = ctk.CTkFrame(
            self.master,
            fg_color=("gray70", "gray20"),  # Light and dark mode colors with transparency
            corner_radius=0,
            border_width=0
        )
        
        # Configure the sidebar
        self.configure(fg_color=UIHelper.HOVER_COLOR)
        
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create content frame
        self.content_frame = ctk.CTkFrame(
            self,
            fg_color=UIHelper.BG_COLOR,
            corner_radius=0,
            width=width
        )
        self.content_frame.grid(row=0, column=0, sticky="nsew")
        self.content_frame.grid_propagate(False)
        
        # Configure content frame grid
        self.content_frame.grid_rowconfigure(1, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Menu title with Material Icons
        self.title_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )
        self.title_frame.grid(row=0, column=0, sticky="ew", pady=(15, 20))
        
        self.menu_icon = ctk.CTkLabel(
            self.title_frame,
            text="menu",  # Material Icons text
            font=("Material Icons", 20),
            text_color=UIHelper.TEXT_COLOR
        )
        self.menu_icon.pack(side="left", padx=10)
        
        self.title_label = ctk.CTkLabel(
            self.title_frame,
            text="MENU",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=UIHelper.TEXT_COLOR
        )
        self.title_label.pack(side="left", padx=5)

        # Menu items container
        self.menu_items_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent",
            corner_radius=0,
            width=width
        )
        self.menu_items_frame.grid(row=1, column=0, sticky="nsew")
        self.menu_items_frame.grid_propagate(False)
        self.menu_items_frame.grid_columnconfigure(0, weight=1)

        # Bind overlay click to hide
        self.overlay.bind("<Button-1>", lambda e: self.hide())
        
        # Initially hide
        self._ensure_hidden()

    def setup_menu_items(self, app):
        """Set up all menu items with their respective app functions"""
        # Define menu items with Material Icons
        self.menu_items = [
            {"icon": "content_cut", "text": "Clipping", "command": app.open_clipping},
            {"icon": "sync", "text": "Converter", "command": app.show_main_page},
            {"icon": "download", "text": "Downloads", "command": app.open_downloads},
            {"icon": "settings", "text": "Settings", "command": app.open_settings},
            {"icon": "palette", "text": "Themes", "command": app.open_themes},
            {"icon": "bar_chart", "text": "Statistics", "command": app.open_statistics},
            {"icon": "info", "text": "About", "command": app.open_about},
            {"icon": "help", "text": "Help", "command": app.open_help}
        ]

        # Clear existing menu items
        for widget in self.menu_items_frame.winfo_children():
            widget.destroy()

        # Create menu items
        for i, item in enumerate(self.menu_items):
            menu_item = self._create_menu_item(
                self.menu_items_frame,
                item["icon"],
                item["text"],
                lambda cmd=item["command"]: [cmd(), self.hide()]
            )
            menu_item.grid(row=i, column=0, sticky="ew", padx=5, pady=2)
            
        # Configure rows for menu items
        for i in range(len(self.menu_items)):
            self.menu_items_frame.grid_rowconfigure(i, weight=0)

    def _create_menu_item(self, parent, icon, text, command):
        """Create a menu item with Material Icons"""
        frame = ctk.CTkFrame(
            parent,
            fg_color="transparent",
            corner_radius=8
        )
        
        # Icon using Material Icons font
        icon_label = ctk.CTkLabel(
            frame,
            text=icon,
            font=("Material Icons", 20),
            text_color=UIHelper.TEXT_COLOR
        )
        icon_label.pack(side="left", padx=10)
        
        # Text label
        text_label = ctk.CTkLabel(
            frame,
            text=text,
            font=ctk.CTkFont(size=13),
            text_color=UIHelper.TEXT_COLOR
        )
        text_label.pack(side="left", padx=5)
        
        # Make the entire frame clickable
        frame.bind("<Button-1>", lambda e: command())
        frame.bind("<Enter>", lambda e: frame.configure(fg_color=UIHelper.HOVER_COLOR))
        frame.bind("<Leave>", lambda e: frame.configure(fg_color="transparent"))
        
        return frame

    def show(self):
        """Show the sidebar"""
        if not self.visible:
            self.visible = True
            # Place the overlay first
            self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
            # Place the sidebar on the left side
            self.place(relx=0, rely=0, relheight=1.0, width=self.width)

    def hide(self):
        """Hide the sidebar"""
        if self.visible:
            self.visible = False
            self.place_forget()
            self.overlay.place_forget()

    def toggle(self):
        """Toggle sidebar visibility"""
        if self.visible:
            self.hide()
        else:
            self.show()

    def _ensure_hidden(self):
        """Ensure the sidebar is completely hidden"""
        self.visible = False
        self.place_forget()
        self.overlay.place_forget()

    def _update_position(self, show: bool):
        """Update sidebar position"""
        if show:
            self.place(relx=0, rely=0, relheight=1.0, width=self.width)
        else:
            self.place_forget()
