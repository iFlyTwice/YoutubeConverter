import customtkinter as ctk
from PIL import Image
import os
import time
import threading
from components.sidebar import SmoothSidebar
from components.settings_page import SettingsPage
from components.main_page import MainPage
from components.about_page import AboutPage
from components.help_page import HelpPage
from components.themes_page import ThemesPage
from components.statistics_page import StatisticsPage
from components.downloads_page import DownloadsPage
from utils.settings_manager import SettingsManager
import json

# Set the appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Colors
DARKER_COLOR = "#1a1a1a"
ACCENT_COLOR = "#3d3d3d"
HOVER_COLOR = "#4d4d4d"
TEXT_COLOR = "#ffffff"

class YoutubeConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Initialize settings manager
        self.settings_manager = SettingsManager()
        
        # Configure window
        self.title("Modern YouTube Converter")
        
        # Load window geometry from settings
        settings = self.settings_manager.load_settings()
        width = settings.get("window", {}).get("width", 800)  # Default to smaller width
        height = settings.get("window", {}).get("height", 500)  # Default to smaller height
        x = settings.get("window", {}).get("x")
        y = settings.get("window", {}).get("y")
        
        # Set initial geometry
        geometry = f"{width}x{height}"
        if x is not None and y is not None:
            geometry += f"+{x}+{y}"
        self.geometry(geometry)
        
        # Set minimum window size to allow for smaller sizes while keeping UI usable
        self.minsize(400, 300)
        
        # Configure grid weights for better resizing
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)  # Give more weight to main content
        self.grid_columnconfigure(0, weight=1)  # Less weight for sidebar
        
        # Apply always-on-top setting
        always_on_top = self.settings_manager.get_setting('always_on_top', False)
        self.attributes('-topmost', always_on_top)
        
        # Set theme
        self.theme = self.settings_manager.get_setting('theme', 'Dark')
        
        # Window attributes
        self._focused_widget = None
        
        # Set window color
        self._set_appearance_mode("dark")
        self.configure(fg_color=DARKER_COLOR)

        # Create main container with reduced padding
        self.main_container = ctk.CTkFrame(self, fg_color=DARKER_COLOR)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create header frame
        self.header_frame = ctk.CTkFrame(self.main_container, fg_color=DARKER_COLOR)
        self.header_frame.pack(fill="x")

        # Create and style the title label
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="YouTube Converter",
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color="#ffffff",
            compound="left"
        )
        self.title_label.pack(side="left", padx=20, pady=15)

        # Add shadow effect to title
        shadow_label = ctk.CTkLabel(
            self.header_frame,
            text="YouTube Converter",
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color="gray20",
            compound="left"
        )
        shadow_label.place(in_=self.title_label, x=2, y=2)
        self.title_label.lift()  # Bring main text to front

        # Create button frame for top-right buttons with padding
        button_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        button_frame.pack(side="right", padx=10)

        # Menu toggle button using label
        self.hamburger_button = ctk.CTkLabel(
            button_frame,
            text="☰",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=TEXT_COLOR,
            fg_color="transparent",
            cursor="hand2"  # Show hand cursor on hover
        )
        self.hamburger_button.pack(side="right", padx=10)
        
        # Bind click and hover events
        self.hamburger_button.bind("<Button-1>", lambda e: self.toggle_menu())
        self.hamburger_button.bind("<Enter>", lambda e: self.hamburger_button.configure(text_color="#999999"))
        self.hamburger_button.bind("<Leave>", lambda e: self.hamburger_button.configure(text_color=TEXT_COLOR))

        # Create content frame
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color=DARKER_COLOR)
        self.content_frame.pack(fill="both", expand=True)

        # Create sidebar
        self.sidebar = SmoothSidebar(self)

        # Main content area
        self.main_frame = ctk.CTkFrame(self.content_frame, fg_color=DARKER_COLOR)
        self.main_frame.pack(fill="both", expand=True)

        # Initialize UI components
        self.setup_menu()
        
        # Initialize main page
        self.main_page = MainPage(self.main_frame, fg_color=DARKER_COLOR)
        self.main_page.pack(fill="both", expand=True)

    def _on_configure(self, event):
        """Handle window configuration changes"""
        # Save window position and size to settings
        if not self.winfo_exists():
            return
            
        geometry = {
            'width': self.winfo_width(),
            'height': self.winfo_height(),
            'x': self.winfo_x(),
            'y': self.winfo_y()
        }
        self.settings_manager.update_setting('window', geometry)

    def setup_menu(self):
        """Set up the sidebar menu items"""
        menu_items = [
            ("⚙️", "Settings", self.open_settings),
            ("📥", "Downloads", self.open_downloads),
            ("🎨", "Themes", self.open_themes),
            ("📊", "Statistics", self.open_statistics),
            (" ℹ️", "About", self.open_about),
            ("❔", "Help", self.open_help)
        ]

        for icon, text, command in menu_items:
            self.sidebar.add_menu_item(icon, text, command)

    def toggle_menu(self):
        self.sidebar.toggle()

    def toggle_always_on_top(self, event=None):
        """Toggle the always-on-top state of the window"""
        current_state = self.settings_manager.get_setting('always_on_top', False)
        new_state = not current_state
        
        # Update window state immediately
        self.attributes('-topmost', new_state)
        if new_state:
            # Force window to stay on top by lifting it
            self.lift()
            self.focus_force()
        
        # Save to settings
        self.settings_manager.update_setting('always_on_top', new_state)

    def switch_page(self, page_class):
        """Switch to a new page"""
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Create and pack new page
        new_page = page_class(self.main_frame, fg_color=DARKER_COLOR)
        new_page.pack(fill="both", expand=True)

    def open_settings(self):
        """Open the settings page"""
        # Hide the sidebar first
        if self.sidebar.visible:
            self.sidebar.toggle()
            
        self.switch_page(SettingsPage)

    def open_downloads(self):
        """Open the downloads page"""
        # Hide the sidebar first
        if self.sidebar.visible:
            self.sidebar.toggle()
        
        self.transition_to_page(DownloadsPage)

    def open_themes(self):
        """Open the themes settings"""
        # Hide the sidebar first
        if self.sidebar.visible:
            self.sidebar.toggle()
        
        self.transition_to_page(ThemesPage)

    def open_statistics(self):
        """Open the statistics page"""
        # Hide the sidebar first
        if self.sidebar.visible:
            self.sidebar.toggle()
        
        self.transition_to_page(StatisticsPage)

    def open_about(self):
        """Open the about page"""
        # Hide the sidebar first
        if self.sidebar.visible:
            self.sidebar.toggle()
        
        self.transition_to_page(AboutPage)

    def open_help(self):
        """Open the help page"""
        # Hide the sidebar first
        if self.sidebar.visible:
            self.sidebar.toggle()
        
        self.transition_to_page(HelpPage)

    def transition_to_page(self, page_class, **kwargs):
        """Handle clean transition between pages"""
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Prepare common kwargs
        page_kwargs = {
            "master": self.main_frame,
            "fg_color": DARKER_COLOR,
            "app": self
        }
        
        # Add back button callback for pages that need it
        if page_class in [DownloadsPage, AboutPage, HelpPage, StatisticsPage, ThemesPage, SettingsPage]:
            page_kwargs["on_back_click"] = self.show_main_page
            
        # Create and pack new page
        new_page = page_class(**page_kwargs)
        new_page.pack(fill="both", expand=True)
        
        return new_page
        
    def show_main_page(self):
        """Switch to main page"""
        # Hide the sidebar first if visible
        if self.sidebar.visible:
            self.sidebar.toggle()
        return self.transition_to_page(MainPage)

    def on_closing(self):
        """Handle window closing event"""
        # Save window geometry
        settings = self.settings_manager.load_settings()
        if "window" not in settings:
            settings["window"] = {}
            
        settings["window"].update({
            "width": self.winfo_width(),
            "height": self.winfo_height(),
            "x": self.winfo_x(),
            "y": self.winfo_y()
        })
        
        self.settings_manager.save_settings(settings)
        self.quit()

if __name__ == "__main__":
    app = YoutubeConverterApp()
    app.mainloop()
