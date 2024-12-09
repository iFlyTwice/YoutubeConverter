import os
import sys

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

import logging
import customtkinter as ctk
import json
from typing import Optional, Dict, Any
from PIL import Image
import threading
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up logging directory
log_dir = os.path.join(current_dir, 'logs')
os.makedirs(log_dir, exist_ok=True)

from config.themes import (
    ThemeManager, ThemeColors, THEMES,
    update_widget_tree
)

from components.main_page import MainPage
from components.settings_page import SettingsPage
from components.themes_page import ThemesPage
from components.sidebar import Sidebar
from components.about_page import AboutPage
from components.help_page import HelpPage
from components.downloads_page import DownloadsPage
from components.clipping_page import ClippingPage
from components.statistics_page import StatisticsPage
from components.notification_popover import NotificationPopover
from ui_helper import UIHelper
from utils.settings_manager import SettingsManager

# Set the appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Constants
DARKER_COLOR = "#1a1a1a"
ACCENT_COLOR = "#3d3d3d"
HOVER_COLOR = "#4d4d4d"
TEXT_COLOR = "#ffffff"

class YoutubeConverterApp(ctk.CTk):
    def __init__(self):
        """Initialize the YouTube Converter application."""
        super().__init__()
        
        # Initialize theme manager and load theme
        self.theme_manager = ThemeManager()
        loaded_theme = self.theme_manager.load_theme()
        self.theme = loaded_theme if isinstance(loaded_theme, ThemeColors) else THEMES["Dark Mode"]
        
        # Initialize variables for sidebar animation
        self.sidebar_visible = False
        self.animating = False
        
        # Load Material Icons font
        fonts_dir = os.path.join(current_dir, 'fonts')
        self.tk.call('lappend', 'auto_path', fonts_dir)
        self.tk.call('source', os.path.join(fonts_dir, 'material-icons.tcl'))
        
        # Initialize settings manager
        self.settings_manager = SettingsManager()
        
        # Initialize current_page
        self.current_page = None
        
        # Configure window
        self.title("YouPro - v1.0.2")  # Update window title
        self.geometry("800x600")
        self.corner_radius = 15  # Add rounded corners to the main window
        self.minsize(800, 600)
        self.configure(fg_color=self.theme.bg)
        self.overrideredirect(True)  # Remove title bar
        
        # Set window attributes to show in taskbar and enable minimize/restore
        self.after(10, lambda: self.wm_attributes("-toolwindow", 0))
        self.after(10, lambda: self.wm_attributes("-topmost", 0))
        
        # Set window title
        self.title("YouPro - v1.0.2")
        
        # Register this as a normal window with the system
        self.wm_attributes("-alpha", 1.0)
        self.wm_attributes("-transparentcolor", "")
        
        # Make window draggable
        self.bind("<Map>", self._on_map)
        
        # Configure grid weights for better resizing
        self.grid_rowconfigure(0, weight=0)  # Title bar row
        self.grid_rowconfigure(1, weight=0)  # Header row
        self.grid_rowconfigure(2, weight=1)  # Main content row
        self.grid_columnconfigure(0, weight=1)  # Single column for main content

        self._create_title_bar()
        self._create_header()

        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color=DARKER_COLOR)
        self.main_container.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure main container grid
        self.main_container.grid_rowconfigure(1, weight=1)  # Content row
        self.main_container.grid_columnconfigure(0, weight=1)  # Single column
        
        # Content frame
        self.content_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=DARKER_COLOR,
            corner_radius=15  # Add rounded corners to the content frame
        )
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=(5, 2), pady=0)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Main content area
        self.main_frame = ctk.CTkFrame(self.content_frame, fg_color=DARKER_COLOR)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Initialize UI components
        self.setup_theme()
        self.setup_main_page()
        
        # Create sidebar menu (initially hidden)
        self.sidebar = Sidebar(self)
        self.sidebar.place(relx=1.0, rely=0, relheight=1, anchor="ne")  # Place it completely off-screen
        self.sidebar.place_forget()  # Hide it completely
        
        # Add menu items with correct icons and commands
        self.sidebar.add_menu_item("Home", "🏠", self.show_main_page)
        self.sidebar.add_menu_item("Settings", "⚙️", self.open_settings)
        self.sidebar.add_menu_item("Downloads", "📥", self.open_downloads)
        self.sidebar.add_menu_item("Themes", "🎨", self.open_themes)
        self.sidebar.add_menu_item("Clipping", "✂️", self.open_clipping)
        self.sidebar.add_menu_item("Statistics", "📊", self.open_statistics)
        self.sidebar.add_menu_item("About", "ℹ️", self.open_about)
        self.sidebar.add_menu_item("Help", "❓", self.open_help)
        
    def _create_title_bar(self) -> None:
        """Create custom title bar"""
        # Create title bar frame with modern styling
        self.title_bar = UIHelper.create_section_frame(
            self,
            height=32,  # Standard Windows title bar height
            fg_color="#2d2d2d",  # Darker background
            corner_radius=8
        )
        self.title_bar.grid(row=0, column=0, sticky="new", padx=5, pady=5)
        self.title_bar.grid_propagate(False)
        self.title_bar.grid_columnconfigure(1, weight=1)

        # Title text
        self.title_text = ctk.CTkLabel(
            self.title_bar,
            text="YouPro - v1.0.1",
            font=ctk.CTkFont(size=12),
            text_color="#808080"
        )
        self.title_text.grid(row=0, column=0, padx=10, sticky="w")

        # Window controls frame
        self.controls_frame = ctk.CTkFrame(
            self.title_bar,
            fg_color="transparent",
            height=32,
            corner_radius=8
        )
        self.controls_frame.grid(row=0, column=2, sticky="e")

        # Create draggable area
        self.drag_area = ctk.CTkFrame(
            self.title_bar,
            fg_color="transparent",
            height=32,
            corner_radius=8
        )
        self.drag_area.grid(row=0, column=1, sticky="ew")

        # Make title bar draggable
        self._drag_start_x = 0
        self._drag_start_y = 0
        
        # Bind drag events
        for widget in [self.title_bar, self.drag_area, self.title_text]:
            widget.bind("<Button-1>", self.start_drag)
            widget.bind("<B1-Motion>", self.on_drag)

        # Window control buttons
        button_color = "#2d2d2d"
        hover_color = "#3d3d3d"
        
        self.min_button = ctk.CTkButton(
            self.controls_frame,
            text="—",
            width=45,
            height=32,
            command=self.minimize_window,
            fg_color=button_color,
            hover_color=hover_color,
            corner_radius=0
        )
        self.min_button.pack(side="left")

        self.close_button = ctk.CTkButton(
            self.controls_frame,
            text="✕",
            width=45,
            height=32,
            command=self.close_window,
            fg_color=button_color,
            hover_color="#c42b1c",
            corner_radius=0
        )
        self.close_button.pack(side="left")
    
    def _create_header(self) -> None:
        """Create the header with menu button and title"""
        # Create header frame
        self.header_frame = ctk.CTkFrame(self, fg_color=DARKER_COLOR, height=60)
        self.header_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        self.header_frame.grid_columnconfigure(1, weight=1)
        self.header_frame.grid_propagate(False)
        
        # Menu button
        self.menu_button = ctk.CTkButton(
            self.header_frame,
            text="☰",
            width=40,
            height=40,
            command=self.toggle_sidebar,
            fg_color="transparent",
            hover_color="#2a2a2a",
            font=ctk.CTkFont(size=20)
        )
        self.menu_button.grid(row=0, column=0, padx=(10, 0), pady=10)
        
        # Title with yellow text and underline
        title_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        title_frame.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=10)
        
        # Title label
        title_label = ctk.CTkLabel(
            title_frame,
            text="YouPro",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#f0b500"  # Yellow color
        )
        title_label.pack(anchor="w", pady=(0, 2))
        
        # Underline
        underline = ctk.CTkFrame(
            title_frame,
            height=2,
            fg_color="#f0b500",  # Same yellow color
            corner_radius=0
        )
        underline.pack(fill="x")

    def animate_sidebar(self, show: bool):
        """Animate the sidebar in or out"""
        if self.animating:
            return
            
        self.animating = True
        start_x = 1.2 if show else 1.0
        end_x = 1.0 if show else 1.2
        steps = 20
        step_size = (end_x - start_x) / steps
        
        def animate_step(current_step):
            if current_step >= steps:
                self.sidebar_visible = show
                self.animating = False
                if not show:
                    self.sidebar.place_forget()
                return
            
            current_x = start_x + (step_size * current_step)
            self.sidebar.place(relx=current_x, rely=0, relheight=1, anchor="ne")
            self.after(10, lambda: animate_step(current_step + 1))
        
        animate_step(0)
    
    def toggle_sidebar(self):
        """Toggle the sidebar with animation"""
        if not hasattr(self, 'sidebar_visible'):
            self.sidebar_visible = False
            
        if not self.sidebar_visible:
            # Show sidebar before animation
            self.sidebar.place(relx=1.0, rely=0, relheight=1, anchor="ne")
            self.animate_sidebar(True)
        else:
            self.animate_sidebar(False)
    
    def hide_sidebar(self):
        """Hide the sidebar with animation"""
        if self.sidebar_visible and not self.animating:
            self.animate_sidebar(False)

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
        """Open the Settings page."""
        logger = logging.getLogger(__name__)
        logger.info("Opening Settings page")
        self.hide_sidebar()
        self.transition_to_page(SettingsPage)

    def open_downloads(self):
        """Open the Downloads page."""
        logger = logging.getLogger(__name__)
        logger.info("Opening Downloads page")
        self.hide_sidebar()
        self.transition_to_page(DownloadsPage)

    def open_statistics(self):
        """Open the Statistics page."""
        logger = logging.getLogger(__name__)
        logger.info("Opening Statistics page")
        self.hide_sidebar()
        self.transition_to_page(StatisticsPage)

    def open_clipping(self):
        """Open the Clipping page."""
        logger = logging.getLogger(__name__)
        logger.info("Opening Clipping page")
        self.hide_sidebar()
        self.transition_to_page(ClippingPage)

    def open_themes(self):
        """Open the Themes page."""
        logger = logging.getLogger(__name__)
        logger.info("Opening Themes page")
        self.hide_sidebar()
        self.transition_to_page(ThemesPage)

    def open_about(self):
        """Open the About page."""
        logger = logging.getLogger(__name__)
        logger.info("Opening About page")
        self.hide_sidebar()
        self.transition_to_page(AboutPage)

    def open_help(self):
        """Open the Help page."""
        logger = logging.getLogger(__name__)
        logger.info("Opening Help page")
        self.hide_sidebar()
        self.transition_to_page(HelpPage)

    def show_main_page(self):
        """Switch to main page"""
        logger = logging.getLogger(__name__)
        logger.info("Switching to Main page")
        # Hide the sidebar first if visible
        if self.sidebar_visible:
            logger.debug("Hiding sidebar before transition")
            self.hide_sidebar()
        return self.transition_to_page(MainPage)

    def transition_to_page(self, page_class) -> None:
        """
        Transition to a new page.

        Args:
            page_class: The class of the page to transition to
        """
        try:
            logger.info(f"Opening {page_class.__name__}")
            
            # Clear current page if it exists
            if self.current_page:
                self.current_page.destroy()

            # Create and show new page
            self.current_page = page_class(self.main_frame, app=self)  # Use main_frame as parent
            self.current_page.grid(row=0, column=0, sticky="nsew")  # Use grid instead of pack
            
            # Apply current theme if it exists
            if hasattr(self, 'theme') and isinstance(self.theme, ThemeColors):
                # Apply theme to the page frame itself
                self.current_page.configure(fg_color=self.theme.bg)
                # Update all widgets within the page
                update_widget_tree(self.current_page, self.theme)
            else:
                # Load default theme if current theme is invalid
                self.theme = THEMES["Dark Mode"]
                self.current_page.configure(fg_color=self.theme.bg)
                update_widget_tree(self.current_page, self.theme)
            
            logger.info(f"Successfully transitioned to {page_class.__name__}")
            
        except Exception as e:
            logger.error(f"Error transitioning to {page_class.__name__}: {e}")

    def on_closing(self):
        """Handle application closing."""
        try:
            # Save current theme
            if hasattr(self, 'theme'):
                self.theme_manager.save_theme(self.theme)
            
            # Destroy the window
            self.quit()
            self.destroy()
        except Exception as e:
            logger.error(f"Error during app closing: {e}")
            self.destroy()

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

    def minimize_window(self):
        """Minimize the window"""
        try:
            self.update_idletasks()
            self.state('iconic')
        except Exception as e:
            logger.error(f"Error minimizing window: {e}")

    def toggle_maximize(self):
        """Toggle between maximized and normal window state"""
        if self.attributes('-zoomed'):
            self.attributes('-zoomed', False)
        else:
            self.attributes('-zoomed', True)

    def _on_map(self, event=None):
        """Handle window mapping event to ensure proper window behavior"""
        # Ensure window appears in taskbar
        if self.state() == "withdrawn":
            self.deiconify()
        self.update_idletasks()
        
        # Re-apply window attributes
        self.wm_attributes("-toolwindow", 0)
        self.wm_attributes("-topmost", 0)
        
        # Restore override redirect
        self.overrideredirect(True)

    def close_window(self):
        """Close the window"""
        self.quit()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

if __name__ == "__main__":
    app = YoutubeConverterApp()
    app.mainloop()
