import os
import sys

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_dir not in sys.path:
    sys.path.append(project_dir)

import json
import threading
import logging
import customtkinter as ctk
from PIL import Image
from ui_helper import UIHelper
from components.main_page import MainPage
from components.sidebar import SmoothSidebar
from utils.settings_manager import SettingsManager
from components.settings_page import SettingsPage
from components.about_page import AboutPage
from components.help_page import HelpPage
from components.downloads_page import DownloadsPage
from components.clipping_page import ClippingPage
from components.themes_page import ThemesPage
from components.statistics_page import StatisticsPage
from datetime import datetime

# Set up logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f'youtube_converter_{datetime.now().strftime("%Y%m%d")}.log')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()  # Also log to console
    ]
)

logger = logging.getLogger(__name__)
logger.info("Starting YouTube Converter application")

# Set the appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Constants
DARKER_COLOR = "#121212"
ACCENT_COLOR = "#3d3d3d"
HOVER_COLOR = "#4d4d4d"
TEXT_COLOR = "#ffffff"

class YoutubeConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Load Material Icons font
        fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
        self.tk.call('lappend', 'auto_path', fonts_dir)
        self.tk.call('source', os.path.join(fonts_dir, 'material-icons.tcl'))
        
        # Initialize settings manager
        self.settings_manager = SettingsManager()
        
        # Initialize current_page
        self.current_page = None
        
        # Configure window
        self.title("Modern YouTube Converter")
        self.geometry("1000x600")
        self.minsize(800, 500)
        self.overrideredirect(True)  # Remove title bar
        
        # Set window attributes to show in taskbar and enable minimize/restore
        self.after(10, lambda: self.wm_attributes("-toolwindow", 0))
        self.after(10, lambda: self.wm_attributes("-topmost", 0))
        
        # Set window title
        self.title("YouTube Converter")
        
        # Register this as a normal window with the system
        self.wm_attributes("-alpha", 1.0)
        self.wm_attributes("-transparentcolor", "")
        
        # Make window draggable
        self.bind("<Map>", self._on_map)
        
        # Configure grid weights for better resizing
        self.grid_rowconfigure(0, weight=0)  # Title bar row
        self.grid_rowconfigure(1, weight=1)  # Main content row
        self.grid_columnconfigure(0, weight=1)  # Single column for main content

        # Create title bar frame with smaller corner radius
        self.title_bar = UIHelper.create_section_frame(
            self,
            height=25,
            fg_color="#1a1a1a",
            corner_radius=8
        )
        self.title_bar.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        
        # Configure title bar grid
        self.title_bar.grid_columnconfigure(1, weight=1)  # Middle space takes most room
        
        # Window controls frame (left side)
        self.controls_frame = ctk.CTkFrame(self.title_bar, fg_color="transparent")
        self.controls_frame.grid(row=0, column=0, sticky="w", padx=0)
        
        # Minimize and close buttons
        self.close_button = ctk.CTkLabel(
            self.controls_frame, 
            text="×",
            width=25,
            height=25,
            fg_color="transparent",
            text_color="#ffffff",
            cursor="hand2"
        )
        self.close_button.grid(row=0, column=1, padx=0)
        self.close_button.bind("<Button-1>", lambda e: self.quit())
        self.close_button.bind("<Enter>", lambda e: self.close_button.configure(fg_color="#aa0000"))
        self.close_button.bind("<Leave>", lambda e: self.close_button.configure(fg_color="transparent"))
        
        self.min_button = ctk.CTkLabel(
            self.controls_frame, 
            text="─",
            width=25,
            height=25,
            fg_color="transparent",
            text_color="#ffffff",
            cursor="hand2"
        )
        self.min_button.grid(row=0, column=0, padx=0)
        self.min_button.bind("<Button-1>", lambda e: self.minimize_window())
        self.min_button.bind("<Enter>", lambda e: self.min_button.configure(fg_color="#333333"))
        self.min_button.bind("<Leave>", lambda e: self.min_button.configure(fg_color="transparent"))

        # Make title bar draggable
        self._drag_start_x = 0
        self._drag_start_y = 0
        
        # Bind drag events to title bar and its children
        for widget in [self.title_bar, self.controls_frame]:
            widget.bind("<Button-1>", self.start_drag)
            widget.bind("<B1-Motion>", self.on_drag)
            
        # Create a draggable area in the middle of the title bar
        self.drag_area = ctk.CTkFrame(
            self.title_bar,
            fg_color="transparent",
            height=25
        )
        self.drag_area.grid(row=0, column=1, sticky="ew")
        self.drag_area.bind("<Button-1>", self.start_drag)
        self.drag_area.bind("<B1-Motion>", self.on_drag)

        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color=DARKER_COLOR)
        self.main_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure main container grid
        self.main_container.grid_rowconfigure(1, weight=1)  # Content row
        self.main_container.grid_columnconfigure(0, weight=1)  # Single column
        
        # Header frame
        self.header_frame = ctk.CTkFrame(self.main_container, fg_color=DARKER_COLOR)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header_frame.grid_columnconfigure(1, weight=1)  # Title takes remaining space
        
        # Title label
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="YouTube Converter",
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color="#ffffff",
            compound="left"
        )
        self.title_label.grid(row=0, column=0, sticky="w", padx=20, pady=15)
        
        # Menu button frame
        button_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        button_frame.grid(row=0, column=2, sticky="e", padx=10)
        
        # Menu toggle button
        self.hamburger_button = ctk.CTkLabel(
            button_frame,
            text="☰",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#808080",
            fg_color="transparent",
            cursor="hand2"
        )
        self.hamburger_button.grid(row=0, column=0, padx=10)
        self.hamburger_button.bind("<Button-1>", lambda e: self.toggle_menu())
        self.hamburger_button.bind("<Enter>", lambda e: self.hamburger_button.configure(text_color="#999999"))
        self.hamburger_button.bind("<Leave>", lambda e: self.hamburger_button.configure(text_color="#808080"))
        
        # Content frame
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color=DARKER_COLOR)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=(5, 2), pady=0)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Create sidebar but don't show it
        self.sidebar = SmoothSidebar(self)
        self.sidebar.visible = False  # Ensure visibility flag is set correctly
        self.sidebar.setup_menu_items(self)  # Setup menu items after hiding
        
        # Main content area
        self.main_frame = ctk.CTkFrame(self.content_frame, fg_color=DARKER_COLOR)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Initialize UI components
        self.setup_theme()
        self.setup_main_page()
        
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
        """Setup the menu sidebar"""
        self.sidebar.setup_menu_items(self)
        # Ensure sidebar stays hidden after setup
        self.sidebar.place_forget()
        
    def toggle_menu(self):
        """Toggle the sidebar menu"""
        if hasattr(self, 'sidebar'):
            logger.debug("Toggle menu called. Sidebar visible before toggle: %s", self.sidebar.visible)
            self.sidebar.toggle()
            logger.debug("Sidebar visible after toggle: %s", self.sidebar.visible)
        
    def load_icon(self, name):
        """Load an icon image"""
        try:
            return ctk.CTkImage(
                light_image=Image.open(f"assets/icons/{name}.png"),
                dark_image=Image.open(f"assets/icons/{name}.png"),
                size=(20, 20)
            )
        except Exception as e:
            print(f"Error loading icon {name}: {e}")
            return None

    def setup_theme(self):
        """Set up the theme"""
        # Set theme
        self.theme = self.settings_manager.get_setting('theme', 'Dark')
        
        # Set window color
        self._set_appearance_mode("dark")
        self.configure(fg_color=DARKER_COLOR)

    def setup_main_page(self):
        """Set up the main page"""
        # Initialize main page using transition_to_page
        self.current_page = MainPage(self.main_frame, app=self, fg_color=DARKER_COLOR)
        self.current_page.pack(fill="both", expand=True)

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
        logger = logging.getLogger(__name__)
        logger.info("Opening Settings page")
        # Hide the sidebar first
        if self.sidebar.visible:
            logger.debug("Hiding sidebar before transition")
            self.sidebar.toggle()
        
        self.transition_to_page(SettingsPage)

    def open_downloads(self):
        """Open the downloads page"""
        logger = logging.getLogger(__name__)
        logger.info("Opening Downloads page")
        # Hide the sidebar first
        if self.sidebar.visible:
            logger.debug("Hiding sidebar before transition")
            self.sidebar.toggle()
        
        self.transition_to_page(DownloadsPage)

    def open_statistics(self):
        """Open the statistics page"""
        logger = logging.getLogger(__name__)
        logger.info("Opening Statistics page")
        # Hide the sidebar first
        if self.sidebar.visible:
            logger.debug("Hiding sidebar before transition")
            self.sidebar.toggle()
        
        self.transition_to_page(StatisticsPage)

    def open_clipping(self):
        """Open the clipping page"""
        logger = logging.getLogger(__name__)
        logger.info("Opening Clipping page")
        # Hide the sidebar first
        if self.sidebar.visible:
            logger.debug("Hiding sidebar before transition")
            self.sidebar.toggle()
        
        self.transition_to_page(ClippingPage)

    def open_themes(self):
        """Open the themes page"""
        logger = logging.getLogger(__name__)
        logger.info("Opening Themes page")
        # Hide the sidebar first
        if self.sidebar.visible:
            logger.debug("Hiding sidebar before transition")
            self.sidebar.toggle()
        
        self.transition_to_page(ThemesPage)

    def open_about(self):
        """Open the about page"""
        logger = logging.getLogger(__name__)
        logger.info("Opening About page")
        # Hide the sidebar first
        if self.sidebar.visible:
            logger.debug("Hiding sidebar before transition")
            self.sidebar.toggle()
        
        self.transition_to_page(AboutPage)

    def open_help(self):
        """Open the help page"""
        logger = logging.getLogger(__name__)
        logger.info("Opening Help page")
        # Hide the sidebar first
        if self.sidebar.visible:
            logger.debug("Hiding sidebar before transition")
            self.sidebar.toggle()
        
        self.transition_to_page(HelpPage)

    def show_main_page(self):
        """Switch to main page"""
        logger = logging.getLogger(__name__)
        logger.info("Switching to Main page")
        # Hide the sidebar first if visible
        if self.sidebar.visible:
            logger.debug("Hiding sidebar before transition")
            self.sidebar.toggle()
        return self.transition_to_page(MainPage)

    def transition_to_page(self, page_class, **kwargs):
        """Handle clean transition between pages"""
        logger = logging.getLogger(__name__)
        logger.info(f"Transitioning from {self.current_page.__class__.__name__ if hasattr(self, 'current_page') else 'None'} to {page_class.__name__}")
        
        # Remove current page if it exists
        if hasattr(self, 'current_page'):
            logger.debug(f"Destroying current page: {self.current_page.__class__.__name__}")
            self.current_page.destroy()
        
        # Prepare kwargs for the new page
        page_kwargs = {
            "master": self.main_frame,
            "app": self,  # Pass app reference to all pages
            **kwargs
        }
        
        # Add back button callback for pages that need it
        if page_class in [DownloadsPage, AboutPage, HelpPage, SettingsPage]:
            logger.debug(f"Added back button callback for {page_class.__name__}")
            page_kwargs["on_back_click"] = self.show_main_page
        
        # Create and pack new page
        logger.debug(f"Creating new {page_class.__name__} instance")
        try:
            new_page = page_class(**page_kwargs)
            new_page.pack(fill="both", expand=True)
            
            # Store reference to current page
            self.current_page = new_page
            logger.info(f"Successfully transitioned to {page_class.__name__}")
            
            return new_page
        except Exception as e:
            logger.error(f"Failed to create {page_class.__name__}: {str(e)}")
            raise
        
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

    def start_drag(self, event):
        """Start window drag operation"""
        self._drag_start_x = event.x_root
        self._drag_start_y = event.y_root
        
    def on_drag(self, event):
        """Handle window drag operation"""
        # Calculate the distance moved
        delta_x = event.x_root - self._drag_start_x
        delta_y = event.y_root - self._drag_start_y
        
        # Get the current window position
        x = self.winfo_x() + delta_x
        y = self.winfo_y() + delta_y
        
        # Move the window
        self.geometry(f"+{x}+{y}")
        
        # Update the start position
        self._drag_start_x = event.x_root
        self._drag_start_y = event.y_root

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def minimize_window(self):
        self.iconify()

    def toggle_maximize(self):
        if self.attributes('-zoomed'):
            self.attributes('-zoomed', False)
        else:
            self.attributes('-zoomed', True)

    def _on_map(self, event):
        """Handle window mapping event to ensure proper window behavior"""
        # Ensure window appears in taskbar
        if self.state() == "withdrawn":
            self.deiconify()
        self.update_idletasks()
        
        # Re-apply window attributes
        self.wm_attributes("-toolwindow", 0)
        self.wm_attributes("-topmost", 0)

if __name__ == "__main__":
    app = YoutubeConverterApp()
    app.mainloop()
