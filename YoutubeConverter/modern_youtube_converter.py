import os
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
        
        # Initialize settings manager
        self.settings_manager = SettingsManager()
        
        # Initialize current_page
        self.current_page = None
        
        # Configure window
        self.title("Modern YouTube Converter")
        self.geometry("1000x600")
        self.minsize(800, 500)
        self.overrideredirect(True)  # Remove title bar
        
        # Create title bar frame
        self.title_bar = UIHelper.create_section_frame(
            self,
            height=25,
            fg_color="#1a1a1a",
            corner_radius=0
        )
        self.title_bar.pack(fill="x", side="top", pady=0, padx=0)
        
        # Make window draggable from title bar
        self.title_bar.bind("<Button-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)
        
        # Window controls frame (right-aligned)
        self.controls_frame = ctk.CTkFrame(self.title_bar, fg_color="transparent")
        self.controls_frame.pack(side="right", padx=0)
        
        # Minimize and close buttons
        self.min_button = ctk.CTkLabel(
            self.controls_frame, 
            text="─",
            width=25,
            height=25,
            fg_color="transparent",
            text_color="#ffffff",
            cursor="hand2"
        )
        self.min_button.pack(side="left")
        self.min_button.bind("<Button-1>", lambda e: self.minimize_window())
        self.min_button.bind("<Enter>", lambda e: self.min_button.configure(fg_color="#333333"))
        self.min_button.bind("<Leave>", lambda e: self.min_button.configure(fg_color="transparent"))
        
        self.close_button = ctk.CTkLabel(
            self.controls_frame, 
            text="×",
            width=25,
            height=25,
            fg_color="transparent",
            text_color="#ffffff",
            cursor="hand2"
        )
        self.close_button.pack(side="left")
        self.close_button.bind("<Button-1>", lambda e: self.quit())
        self.close_button.bind("<Enter>", lambda e: self.close_button.configure(fg_color="#aa0000"))
        self.close_button.bind("<Leave>", lambda e: self.close_button.configure(fg_color="transparent"))
        
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
        self.setup_theme()
        self.setup_menu()
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
        # Create sidebar
        self.sidebar.setup_menu_items(self)
        
    def toggle_menu(self):
        """Toggle the sidebar menu"""
        self.sidebar.toggle()
        
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

if __name__ == "__main__":
    app = YoutubeConverterApp()
    app.mainloop()
