import customtkinter as ctk
import threading
import time
from utils.ui_helper import UIHelper

class SmoothSidebar(ctk.CTkFrame):
    def __init__(self, master, width=250, **kwargs):
        # Set width in the constructor and add corner radius
        kwargs["width"] = width
        kwargs["corner_radius"] = 12
        kwargs["border_width"] = 2
        kwargs["border_color"] = "#404040"
        super().__init__(master, **kwargs)
        
        self.width = width
        self.visible = False
        self.animating = False
        self.active_container = None  # Track active menu item
        
        # Configure the sidebar with a darker theme
        self.configure(fg_color="#1a1a1a")
        
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
        # Create container frame for the button
        container = UIHelper.create_section_frame(
            self.content_frame,
            height=45,
            fg_color="transparent",
            corner_radius=0
        )
        container.pack(fill="x", pady=1)
        
        # Create grid layout with minimal spacing
        container.grid_columnconfigure(0, weight=0, minsize=30)
        container.grid_columnconfigure(1, weight=1)
        
        # Add icon with larger font size for emojis
        icon_size = 18
        if icon == "🎬":
            icon_size = 22
            
        icon_label = ctk.CTkLabel(
            container,
            text=icon,
            font=("Segoe UI", icon_size),
            text_color="#ffffff",
            width=30
        )
        icon_label.grid(row=0, column=0, padx=(10, 0))
        
        # Add text right next to icon with consistent padding
        text_label = ctk.CTkLabel(
            container,
            text=text,
            font=("Segoe UI", 14),
            text_color="#ffffff",
            anchor="w"
        )
        text_label.grid(row=0, column=1, sticky="w", padx=(5, 10))
        
        def handle_click(e):
            if self.active_container:
                self.active_container.configure(fg_color="transparent")
            container.configure(fg_color="#2e2e2e")
            self.active_container = container
            if command:
                command()
        
        # Make the entire container clickable
        for widget in [container, icon_label, text_label]:
            widget.bind("<Button-1>", handle_click)
            widget.bind("<Enter>", lambda e: container.configure(fg_color="#2e2e2e" if container != self.active_container else "#2e2e2e"))
            widget.bind("<Leave>", lambda e: container.configure(fg_color="transparent" if container != self.active_container else "#2e2e2e"))
            widget.configure(cursor="hand2")
        
        return container

    def setup_menu_items(self, app):
        """Set up all menu items with emojis"""
        # Add menu items with emojis
        self.add_menu_item("🎬", "Clipping", app.open_clipping)
        self.add_menu_item("🔄", "Converter", app.show_main_page)
        self.add_menu_item("📥", "Downloads", app.open_downloads)
        self.add_menu_item("⚙️", "Settings", app.open_settings)
        self.add_menu_item("🎨", "Themes", app.open_themes)
        self.add_menu_item("📊", "Statistics", app.open_statistics)
        self.add_menu_item("ℹ️", "About", app.open_about)
        self.add_menu_item("❔", "Help", app.open_help)

    def on_sidebar_click(self, event):
        return "break"
        
    def check_click_outside(self, event):
        if not self.visible:
            return
            
        clicked_widget = event.widget
        parent = clicked_widget
        while parent is not None:
            if parent == self:
                return
            parent = parent.master
            
        self.toggle()

    def toggle(self):
        if self.animating:
            return
            
        self.animating = True
        
        if self.visible:
            def hide_animation():
                try:
                    steps = 12
                    start_x = 1.0 - self.width/self.master.winfo_width()
                    end_x = 1.0
                    
                    for i in range(steps + 1):
                        if not self.animating:
                            break
                        t = i / steps
                        t = 1 - (1 - t) * (1 - t)
                        current_x = start_x + (end_x - start_x) * t
                        self.place(relx=current_x, rely=0, relheight=1, x=2)
                        self.update()
                        time.sleep(0.001)
                        
                    self.visible = False
                finally:
                    self.animating = False
                    
            threading.Thread(target=hide_animation, daemon=True).start()
        else:
            def show_animation():
                try:
                    steps = 12
                    start_x = 1.0
                    end_x = 1.0 - self.width/self.master.winfo_width()
                    
                    for i in range(steps + 1):
                        if not self.animating:
                            break
                        t = i / steps
                        t = 1 - (1 - t) * (1 - t)
                        current_x = start_x + (end_x - start_x) * t
                        self.place(relx=current_x, rely=0, relheight=1, x=2)
                        self.update()
                        time.sleep(0.001)
                        
                    self.visible = True
                finally:
                    self.animating = False
                    
            threading.Thread(target=show_animation, daemon=True).start()
