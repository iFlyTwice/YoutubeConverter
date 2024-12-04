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
        self._animation_thread = None
        self._animation_start = None
        self._target_state = None
        
        # Configure the sidebar with a darker theme
        self.configure(fg_color="#1a1a1a")
        
        # Create a container for content with minimal right padding
        self.content_frame = UIHelper.create_section_frame(
            self,
            height=0,  # Let it expand
            fg_color="transparent",
            corner_radius=0
        )
        self.content_frame.pack(fill="both", expand=True, padx=(5, 2))  # Reduced right padding
        
        # Menu title with modern styling
        title_frame = UIHelper.create_section_frame(
            self.content_frame,
            height=50,
            fg_color="transparent",
            corner_radius=0
        )
        title_frame.pack(fill="x", pady=(10, 5))

        # Create centered title text container
        menu_text = UIHelper.create_text_container(
            title_frame,
            title="MENU",
            description="",
            title_font=("Arial", 24, "bold"),
            title_color="#FFFFFF",
            text_align="center"
        )
        menu_text.pack(fill="x", expand=True)

        # Add menu separator
        separator = UIHelper.create_section_frame(
            self.content_frame,
            height=1,  # Thinner line for subtlety
            fg_color="#2e2e2e",  # Lighter color for subtle separation
            corner_radius=0
        )
        separator.pack(fill="x", pady=(15, 15), padx=15)  # Align with menu items

        # Initialize sidebar position
        self.place(relx=1.0, rely=0, relheight=1.0, x=2)
        
        # Bind events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.master.bind("<Configure>", self._on_window_resize)
        self.master.bind("<Button-1>", self._on_click_outside, add="+")

    def _on_enter(self, event):
        """Handle mouse enter event"""
        if not self.animating:
            self.configure(border_color="#505050")

    def _on_leave(self, event):
        """Handle mouse leave event"""
        if not self.animating:
            self.configure(border_color="#404040")

    def _on_click_outside(self, event):
        """Handle clicks outside the sidebar"""
        if not self.visible or self.animating:
            return
            
        # Check if click is inside sidebar
        clicked_widget = event.widget
        parent = clicked_widget
        while parent is not None:
            if parent == self:
                return "break"
            parent = parent.master
            
        # Click was outside, close sidebar
        self.hide()
        return "break"

    def _on_window_resize(self, event=None):
        """Handle window resize events"""
        if not self.animating:
            self._update_position(self.visible)

    def _update_position(self, show: bool):
        """Update sidebar position"""
        x = -self.width if show else 2
        self.place(relx=1.0, rely=0, relheight=1.0, x=x)
        if show:
            self.lift()

    def show(self):
        """Show the sidebar with animation"""
        if self.visible or self.animating:
            return
        self._animate(True)

    def hide(self):
        """Hide the sidebar with animation"""
        if not self.visible or self.animating:
            return
        self._animate(False)

    def toggle(self):
        """Toggle sidebar visibility"""
        if self.animating:
            return
        self._animate(not self.visible)

    def _animate(self, show: bool):
        """Handle sidebar animation
        Args:
            show: True to show sidebar, False to hide
        """
        if self.animating:
            return
            
        self.animating = True
        self._target_state = show
        
        def animate():
            try:
                duration = 0.2  # Animation duration in seconds
                start_time = time.time()
                
                # Set initial position
                start_x = 2 if show else -self.width
                end_x = -self.width if show else 2
                self._update_position(not show)
                
                while True:
                    if not self.animating or self._target_state != show:
                        break
                        
                    current_time = time.time()
                    elapsed = current_time - start_time
                    
                    if elapsed >= duration:
                        # Animation complete
                        self._update_position(show)
                        self.visible = show
                        break
                    
                    # Calculate smooth progress
                    progress = elapsed / duration
                    t = 1 - pow(1 - progress, 3)  # Cubic ease-out
                    
                    # Update position
                    current_x = start_x + (end_x - start_x) * t
                    self.place(relx=1.0, rely=0, relheight=1.0, x=int(current_x))
                    self.update()
                    
                    # Control frame rate
                    time.sleep(0.016)  # ~60fps
                    
            finally:
                self.animating = False
                self._animation_thread = None
                self._target_state = None
        
        self._animation_thread = threading.Thread(target=animate, daemon=True)
        self._animation_thread.start()

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
