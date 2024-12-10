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
        
        # Initialize settings manager first
        self.settings_manager = SettingsManager()
        
        # Initialize theme manager and load theme
        self.theme_manager = ThemeManager()
        
        # Load theme from settings
        theme_data = self.settings_manager.get_setting('theme')
        if isinstance(theme_data, dict):
            self.theme = ThemeColors.from_dict(theme_data)
        else:
            self.theme = THEMES.get(theme_data, THEMES["Dark Mode"]) if isinstance(theme_data, str) else THEMES["Dark Mode"]
        
        # Initialize variables for sidebar animation
        self.sidebar_visible = False
        self.animating = False
        
        # Load Material Icons font
        fonts_dir = os.path.join(current_dir, 'fonts')
        self.tk.call('lappend', 'auto_path', fonts_dir)
        self.tk.call('source', os.path.join(fonts_dir, 'material-icons.tcl'))
        
        # Configure window
        self.title("")  # Remove window title since we're using custom title bar
        self.geometry("800x600")
        self.corner_radius = 15  # Add rounded corners to the main window
        self.minsize(800, 600)
        self.configure(fg_color=self.theme.bg)
        self.overrideredirect(True)  # Remove title bar
        
        # Create title bar frame with border
        self.title_bar = ctk.CTkFrame(
            self, 
            height=30,
            fg_color=self.theme.bg,
            border_width=2,
            border_color="#3f3f3f"
        )
        self.title_bar.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=0, pady=0)
        self.title_bar.grid_propagate(False)
        
        # Configure title bar grid
        self.title_bar.grid_columnconfigure(1, weight=1)  # Middle space takes up most room
        
        # Menu button (left side)
        self.menu_button = ctk.CTkButton(
            self.title_bar,
            text="☰",
            width=30,
            height=30,
            corner_radius=0,
            fg_color="transparent",
            text_color="#ffffff",
            hover_color="#404040",
            font=ctk.CTkFont(size=15),
            command=self.toggle_sidebar
        )
        self.menu_button.grid(row=0, column=0, sticky="w")

        # Control buttons frame (right side)
        self.control_buttons_frame = ctk.CTkFrame(self.title_bar, fg_color="transparent")
        self.control_buttons_frame.grid(row=0, column=2, sticky="e")

        # Minimize button
        self.minimize_button = ctk.CTkButton(
            self.control_buttons_frame,
            text="─",
            width=30,
            height=30,
            corner_radius=0,
            fg_color="transparent",
            text_color="#ffffff",
            hover_color="#404040",
            font=ctk.CTkFont(size=15),
            command=self.minimize_window
        )
        self.minimize_button.grid(row=0, column=0, sticky="e")

        # Close button
        self.close_button = ctk.CTkButton(
            self.control_buttons_frame,
            text="✕",
            width=30,
            height=30,
            corner_radius=0,
            fg_color="transparent",
            text_color="#ffffff",
            hover_color="#FF0000",
            font=ctk.CTkFont(size=15),
            command=self.destroy
        )
        self.close_button.grid(row=0, column=1, sticky="e")

        # Bind dragging events to title bar
        self.title_bar.bind("<Button-1>", self.start_drag)
        self.title_bar.bind("<B1-Motion>", self.on_drag)
        
        # Configure grid weights for better resizing
        self.grid_rowconfigure(0, weight=0)  # Title bar row
        self.grid_rowconfigure(1, weight=0)  # Header row
        self.grid_rowconfigure(2, weight=1)  # Main content row
        self.grid_columnconfigure(0, weight=1)  # Single column for main content

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
        self.apply_theme(self.theme)
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
        
    def _create_header(self) -> None:
        """Create the header with title"""
        # Create header frame
        self.header_frame = ctk.CTkFrame(self, fg_color=DARKER_COLOR, height=60)
        self.header_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        self.header_frame.grid_columnconfigure(0, weight=1)  # Make the title frame expand
        self.header_frame.grid_propagate(False)
        
        # Create title frame
        self.title_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.title_frame.grid(row=0, column=0, sticky="w", padx=20, pady=10)  # Increased left padding
        
        # Title label
        self.title_label = ctk.CTkLabel(
            self.title_frame,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#ffffff"
        )
        self.title_label.pack(side="left", anchor="w")
        
        # Create yellow underline
        self.title_underline = ctk.CTkFrame(
            self.title_frame,
            height=3,
            fg_color="#FFB74D",
            corner_radius=2
        )
        self.title_underline.place(relx=0, rely=0.85, relwidth=0.3)
    
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

    def apply_theme(self, theme: ThemeColors) -> None:
        """
        Apply a theme to the application and save it
        
        Args:
            theme: Theme to apply
        """
        try:
            # Update window colors
            self.configure(fg_color=theme.bg)
            
            # Store theme
            self.theme = theme
            
            # Update header styling
            if hasattr(self, 'title_label'):
                self.title_label.configure(text_color="#ffffff")  # Keep title white for visibility
            if hasattr(self, 'title_underline'):
                self.title_underline.configure(fg_color="#FFB74D")  # Keep accent color consistent
            
            # Update all widgets
            update_widget_tree(self, theme)
            
            # Save theme to settings
            self.settings_manager.update_setting('theme', theme.to_dict())
            
            # Force a redraw
            self.update_idletasks()
            
        except Exception as e:
            logger.error(f"Error applying theme: {e}")

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

    def _check_sidebar_click(self, event):
        """Check if click is outside sidebar and close it if necessary."""
        if not self.sidebar_visible:
            return
            
        # Get sidebar widget coordinates
        sidebar_x = self.sidebar.winfo_rootx()
        sidebar_width = self.sidebar.winfo_width()
        
        # If click is outside sidebar area, close it
        if event.x_root < sidebar_x or event.x_root > (sidebar_x + sidebar_width):
            self.toggle_sidebar()

if __name__ == "__main__":
    app = YoutubeConverterApp()
    app.mainloop()
