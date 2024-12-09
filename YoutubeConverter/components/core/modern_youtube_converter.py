import os
import sys

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root)

import json
import logging
import tkinter as tk
from datetime import datetime
import customtkinter as ctk
from PIL import Image
import threading
from components.notification_popover import NotificationPopover
from components.custom_dropdown import CustomDropdown
from components.tooltip import ModernTooltip
from services.youtube_api import YouTubeAPI

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('youtube_converter.log', mode='a')
    ]
)

logger = logging.getLogger(__name__)
logger.info(f"Starting Modern Youtube Converter application from {project_root}")

import sys
import os

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
components_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(components_dir)
sys.path.append(root_dir)

import customtkinter as ctk
from PIL import Image
import time
import threading
from components.buttons import AnimatedButton, HamburgerButton
from components.sidebar import SmoothSidebar
from components.settings_page import SettingsPage
from components.main_page import MainPage
from components.about_page import AboutPage
from components.help_page import HelpPage
from components.themes_page import ThemesPage
from components.statistics_page import StatisticsPage
from components.downloads_page import DownloadsPage
from components.clip_video_page import ClipVideoPage
from components.notification_popover import NotificationPopover
from components.window_manager import WindowManager
from utils.settings_manager import SettingsManager
import json
from datetime import datetime
import logging

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
        logger.info("Initializing YoutubeConverterApp")
        super().__init__()
        
        # Initialize settings manager
        self.settings_manager = SettingsManager()
        
        # Configure window
        self.title("Modern YouTube Converter")
        self.geometry("900x600")  # Increased initial width
        self.minsize(800, 500)  # Set minimum size to prevent UI elements from being cut off
        
        # Configure window appearance
        self.configure(fg_color="#1e1e1e")
        self.window_manager = WindowManager(self)
        self.window_manager.configure_window()
        
        # Apply always-on-top setting
        always_on_top = self.settings_manager.get_setting('always_on_top', False)
        self.attributes('-topmost', always_on_top)
        
        # Set theme
        self.theme = self.settings_manager.get_setting('theme', 'Dark')
        
        # Window state tracking
        self._is_screenshot_mode = False
        self._window_states = {
            'normal_state': {
                'topmost': False,
                'focus': None,
                'alpha': 1.0
            }
        }
        
        # Bind window events
        self.bind("<Alt-s>", self.toggle_screenshot_mode)
        self.bind("<Alt-t>", self.toggle_always_on_top)
        self.bind("<Escape>", lambda e: self.exit_screenshot_mode())
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        self.bind("<Configure>", self._on_configure)
        self.bind("<Button-1>", self.start_move)
        self.bind("<ButtonRelease-1>", self.stop_move)
        self.bind("<B1-Motion>", self.do_move)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Window attributes
        self._focused_widget = None
        
        # Create main container
        self.main_container = ctk.CTkFrame(self, fg_color="#1a1a1a")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create header frame
        self.header_frame = ctk.CTkFrame(self.main_container, fg_color="#1a1a1a")
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
        button_frame = ctk.CTkFrame(self.header_frame, fg_color="#1a1a1a")
        button_frame.pack(side="right", padx=10)

        # Screenshot button
        self.screenshot_button = AnimatedButton(
            button_frame,
            text="📸",
            width=35,
            height=35,
            fg_color="#2b2b2b",
            hover_color="#3b3b3b",
            command=self.toggle_screenshot_mode,
            tooltip_text="Take Screenshot (Alt+S)",
            font=ctk.CTkFont(size=16)
        )
        self.screenshot_button.pack(side="right", padx=5)

        # Menu toggle button
        self.hamburger_button = HamburgerButton(
            button_frame,
            fg_color="#2b2b2b",
            hover_color="#3b3b3b",
            command=self.toggle_menu
        )
        self.hamburger_button.pack(side="right", padx=5)

        # Initialize app data directory
        self.app_data_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "YoutubeConverter")
        os.makedirs(self.app_data_dir, exist_ok=True)
        logger.debug(f"App data directory: {self.app_data_dir}")
        
        # Create notification button with initial icon
        logger.info("Setting up notification button")
        
        # Create notification button
        self.notification_button = ctk.CTkButton(
            button_frame,
            text="🔔",  # Add bell emoji as default icon
            width=35,
            height=35,
            corner_radius=8,
            fg_color="#2b2b2b",
            hover_color="#3b3b3b",
            command=lambda: self.toggle_notifications(),  # Use lambda to ensure proper binding
            font=ctk.CTkFont(size=16)
        )
        self.notification_button.pack(side="right", padx=5)
        logger.debug("Notification button created")
        
        # Initialize notifications first
        self.notifications = []
        self.unread_notifications = []
        self.load_notifications()
        logger.debug(f"Loaded {len(self.notifications)} notifications")
        
        # Create notification popover
        logger.info("Notification popover initialized")
        self.notification_popover = NotificationPopover(self, self)
        self.notification_popover.withdraw()  # Make sure it's hidden initially
        
        # Update button appearance immediately
        self.update_notification_button()
        
        # Bind click event to handle notification popover
        self.bind("<Button-1>", self.handle_click, add="+")
        
        # Create content frame
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="#1a1a1a")
        self.content_frame.pack(fill="both", expand=True)

        # Create sidebar
        self.sidebar = SmoothSidebar(self)

        # Main content area
        self.main_frame = ctk.CTkFrame(self.content_frame, fg_color="#1a1a1a")
        self.main_frame.pack(fill="both", expand=True)

        # Initialize UI components
        self.setup_menu()
        
        # Initialize main page
        MainPage.open(self.main_frame)
        logger.info("UI setup complete")

    def _save_window_state(self):
        """Save current window state"""
        logger.info("Saving window state")
        self._window_states['normal_state'] = {
            'topmost': self.attributes('-topmost'),
            'focus': self.focus_get(),
            'alpha': self.attributes('-alpha')
        }

    def _restore_window_state(self):
        """Restore previous window state"""
        logger.info("Restoring window state")
        state = self._window_states['normal_state']
        self.attributes('-topmost', state['topmost'])
        self.attributes('-alpha', state['alpha'])
        if state['focus'] and state['focus'].winfo_exists():
            state['focus'].focus_set()

    def _on_configure(self, event):
        """Handle window configuration changes"""
        logger.info("Window configuration changed")
        if hasattr(self, 'overlay') and self.overlay.winfo_exists():
            # Update overlay position to match main window
            x = self.winfo_x()
            y = self.winfo_y()
            width = self.winfo_width()
            height = self.winfo_height()
            self.overlay.geometry(f"{width}x{height}+{x}+{y}")

    def _on_focus_in(self, event):
        """Handle window focus in"""
        logger.info("Window focus in")
        if self._is_screenshot_mode:
            # Ensure window stays on top and visible
            self.attributes('-alpha', 1.0)
            self.attributes('-topmost', True)
            # Bring overlay to front if it exists
            if hasattr(self, 'overlay') and self.overlay.winfo_exists():
                self.overlay.lift()

    def _on_focus_out(self, event):
        """Handle window focus out"""
        logger.info("Window focus out")
        if self._is_screenshot_mode:
            # Keep window visible but slightly transparent when not focused
            self.attributes('-alpha', 0.95)
            self.after(10, lambda: self.attributes('-topmost', True))
            # Ensure overlay stays on top
            if hasattr(self, 'overlay') and self.overlay.winfo_exists():
                self.overlay.lift()
                self.overlay.focus_force()

    def setup_menu(self):
        logger.info("Setting up menu")
        menu_items = [
            ("⚙️", "Settings", self.open_settings),
            ("📂", "Downloads", self.open_downloads),
            ("🎨", "Themes", self.open_themes),
            ("📊", "Statistics", self.open_statistics),
            ("ℹ️", "About", self.open_about),
            ("❓", "Help", self.open_help),
            ("✂️", "Clip Video", self.open_clip_video)
        ]

        for icon, text, command in menu_items:
            self.sidebar.add_menu_item(icon, text, command)

    def toggle_menu(self):
        logger.info("Toggling menu")
        self.sidebar.toggle()

    def toggle_screenshot_mode(self, event=None):
        """Toggle screenshot mode"""
        logger.info("Toggling screenshot mode")
        if self._is_screenshot_mode:
            self.exit_screenshot_mode()
        else:
            self.enter_screenshot_mode()

    def toggle_always_on_top(self, event=None):
        """Toggle the always-on-top state of the window"""
        logger.info("Toggling always-on-top")
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

    def enter_screenshot_mode(self):
        """Enter screenshot mode"""
        logger.info("Entering screenshot mode")
        if self._is_screenshot_mode:
            return
            
        # Save current window state
        self._save_window_state()
        self._is_screenshot_mode = True
        
        # Configure window for screenshot mode
        self.attributes('-topmost', True)
        self.attributes('-alpha', 1.0)
        self.screenshot_button.configure(fg_color="#ff4444")
        
        # Create overlay window
        self.overlay = ctk.CTkToplevel(self)
        self.overlay.title("")
        self.overlay.attributes('-alpha', 0.7)
        self.overlay.attributes('-topmost', True)
        self.overlay.overrideredirect(True)
        
        # Match overlay position
        x = self.winfo_x()
        y = self.winfo_y()
        width = self.winfo_width()
        height = self.winfo_height()
        self.overlay.geometry(f"{width}x{height}+{x}+{y}")

        # Configure overlay
        overlay_frame = ctk.CTkFrame(self.overlay, fg_color="black")
        overlay_frame.pack(fill="both", expand=True)
        
        instructions = ctk.CTkLabel(
            overlay_frame,
            text="Screenshot Mode\n\nPress Alt+S or click the 📸 button again to exit\nPress Escape to cancel",
            font=ctk.CTkFont(size=16),
            text_color="white"
        )
        instructions.pack(expand=True)
        
        # Bind overlay events
        self.overlay.bind("<FocusOut>", self._on_focus_out)
        self.overlay.bind("<Configure>", self._on_configure)
        
        def fade_out():
            if not self._is_screenshot_mode:
                return
            for i in range(7, -1, -1):
                if self._is_screenshot_mode and self.overlay.winfo_exists():
                    self.overlay.attributes('-alpha', i/10)
                    self.overlay.update()
                    self.after(50)
            if hasattr(self, 'overlay') and self.overlay.winfo_exists():
                self.overlay.destroy()
        
        self.after(1000, fade_out)

    def exit_screenshot_mode(self):
        """Exit screenshot mode"""
        logger.info("Exiting screenshot mode")
        if not self._is_screenshot_mode:
            return
            
        self._is_screenshot_mode = False
        self.screenshot_button.configure(fg_color="#3d3d3d")
        
        # Remove overlay
        if hasattr(self, 'overlay') and self.overlay.winfo_exists():
            self.overlay.destroy()
        
        # Restore previous window state
        self._restore_window_state()

    def open_settings(self):
        """Open the settings page"""
        logger.info("Opening settings page")
        # Hide the sidebar first
        if self.sidebar.visible:
            self.sidebar.toggle()
        
        # Create container for animation
        container = ctk.CTkFrame(self.main_frame, fg_color="#1a1a1a")
        container.pack(fill="both", expand=True)

        # Create settings frame starting from right
        settings_frame = ctk.CTkFrame(container, fg_color="#1a1a1a")
        settings_frame.place(relx=1.0, rely=0, relwidth=1, relheight=1)

        # Create main frame for animation
        current_frame = ctk.CTkFrame(container, fg_color="#1a1a1a")
        current_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Move existing content to current frame
        for widget in self.main_frame.winfo_children():
            if widget != container:
                widget.pack_forget()
                widget.pack(in_=current_frame, fill="both", expand=True)

        # Add settings content
        from components.settings_page import SettingsPage
        SettingsPage.open(settings_frame, lambda: self.transition_to_main(container, settings_frame))

        def animate():
            duration = 0.3
            steps = 12
            
            for i in range(steps + 1):
                if not container.winfo_exists():
                    return
                t = i / steps
                t = 1 - (1 - t) * (1 - t)
                
                progress = t
                current_frame.place(relx=-progress, rely=0, relwidth=1, relheight=1)
                settings_frame.place(relx=1-progress, rely=0, relwidth=1, relheight=1)
                container.update()
                time.sleep(0.001)

        # Run animation
        threading.Thread(target=animate, daemon=True).start()

    def show_main_page(self):
        self.transition_to_main()

    def transition_to_main(self, container=None, settings_frame=None):
        """Transition from settings/about/help back to main page"""
        logger.info("Transitioning to main page")
        try:
            if container is None:
                container = self.main_frame
                
            # Create main frame starting from left
            main_frame = ctk.CTkFrame(container, fg_color="#1a1a1a")
            main_frame.place(relx=-1.0, rely=0, relwidth=1, relheight=1)

            # Add main page content
            MainPage.open(main_frame)

            def cleanup_widgets():
                """Safely cleanup widgets"""
                try:
                    if settings_frame and settings_frame.winfo_exists():
                        settings_frame.destroy()
                    if container and container.winfo_exists():
                        for child in container.winfo_children():
                            if child != main_frame and child.winfo_exists():
                                child.destroy()
                except Exception as e:
                    print(f"Cleanup error: {e}")

            def animate():
                try:
                    duration = 0.3
                    steps = 12
                    
                    # Perform the sliding animation
                    for i in range(steps + 1):
                        if not container.winfo_exists():
                            return
                        t = i / steps
                        t = 1 - (1 - t) * (1 - t)
                        
                        progress = t
                        if settings_frame and settings_frame.winfo_exists():
                            settings_frame.place(relx=progress, rely=0, relwidth=1, relheight=1)
                        main_frame.place(relx=-1+progress, rely=0, relwidth=1, relheight=1)
                        container.update()
                        time.sleep(0.001)
                    
                    # Clean up old widgets after animation
                    container.after(100, cleanup_widgets)
                    
                except Exception as e:
                    print(f"Animation error: {e}")
                    cleanup_widgets()

            # Run animation
            threading.Thread(target=animate, daemon=True).start()
            
        except Exception as e:
            print(f"Transition error: {e}")

    def open_downloads(self):
        """Open the downloads page with animation"""
        logger.info("Opening downloads page")
        # Hide the sidebar first
        if self.sidebar.visible:
            self.sidebar.toggle()
        
        # Create container for animation
        container = ctk.CTkFrame(self.main_frame, fg_color="#1a1a1a")
        container.pack(fill="both", expand=True)

        # Create downloads frame starting from right
        downloads_frame = ctk.CTkFrame(container, fg_color="#1a1a1a")
        downloads_frame.place(relx=1.0, rely=0, relwidth=1, relheight=1)

        # Create main frame for animation
        current_frame = ctk.CTkFrame(container, fg_color="#1a1a1a")
        current_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Move existing content to current frame
        for widget in self.main_frame.winfo_children():
            if widget != container:
                widget.pack_forget()
                widget.pack(in_=current_frame, fill="both", expand=True)

        # Add downloads content
        DownloadsPage.open(downloads_frame, lambda: self.transition_to_main(container, downloads_frame))

        def animate():
            duration = 0.3
            steps = 12
            
            for i in range(steps + 1):
                if not container.winfo_exists():
                    return
                t = i / steps
                t = 1 - (1 - t) * (1 - t)
                
                progress = t
                current_frame.place(relx=-progress, rely=0, relwidth=1, relheight=1)
                downloads_frame.place(relx=1-progress, rely=0, relwidth=1, relheight=1)
                container.update()
                time.sleep(0.001)

        # Run animation
        threading.Thread(target=animate, daemon=True).start()

    def open_themes(self):
        """Open the themes settings with animation"""
        logger.info("Opening themes page")
        # Hide the sidebar first
        if self.sidebar.visible:
            self.sidebar.toggle()
        
        # Create container for animation
        container = ctk.CTkFrame(self.main_frame, fg_color="#1a1a1a")
        container.pack(fill="both", expand=True)

        # Create themes frame starting from right
        themes_frame = ctk.CTkFrame(container, fg_color="#1a1a1a")
        themes_frame.place(relx=1.0, rely=0, relwidth=1, relheight=1)

        # Create main frame for animation
        current_frame = ctk.CTkFrame(container, fg_color="#1a1a1a")
        current_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Move existing content to current frame
        for widget in self.main_frame.winfo_children():
            if widget != container:
                widget.pack_forget()
                widget.pack(in_=current_frame, fill="both", expand=True)

        # Add themes content
        ThemesPage.open(themes_frame, lambda: self.transition_to_main(container, themes_frame))

        def animate():
            duration = 0.3
            steps = 12
            
            for i in range(steps + 1):
                if not container.winfo_exists():
                    return
                t = i / steps
                t = 1 - (1 - t) * (1 - t)
                
                progress = t
                current_frame.place(relx=-progress, rely=0, relwidth=1, relheight=1)
                themes_frame.place(relx=1-progress, rely=0, relwidth=1, relheight=1)
                container.update()
                time.sleep(0.001)

        # Run animation
        threading.Thread(target=animate, daemon=True).start()

    def open_statistics(self):
        """Open the statistics page with animation"""
        logger.info("Opening statistics page")
        # Hide the sidebar first
        if self.sidebar.visible:
            self.sidebar.toggle()
        
        # Create container for animation
        container = ctk.CTkFrame(self.main_frame, fg_color="#1a1a1a")
        container.pack(fill="both", expand=True)

        # Create statistics frame starting from right
        statistics_frame = ctk.CTkFrame(container, fg_color="#1a1a1a")
        statistics_frame.place(relx=1.0, rely=0, relwidth=1, relheight=1)

        # Create main frame for animation
        current_frame = ctk.CTkFrame(container, fg_color="#1a1a1a")
        current_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Move existing content to current frame
        for widget in self.main_frame.winfo_children():
            if widget != container:
                widget.pack_forget()
                widget.pack(in_=current_frame, fill="both", expand=True)

        # Add statistics content
        StatisticsPage.open(statistics_frame, lambda: self.transition_to_main(container, statistics_frame))

        def animate():
            duration = 0.3
            steps = 12
            
            for i in range(steps + 1):
                if not container.winfo_exists():
                    return
                t = i / steps
                t = 1 - (1 - t) * (1 - t)
                
                progress = t
                current_frame.place(relx=-progress, rely=0, relwidth=1, relheight=1)
                statistics_frame.place(relx=1-progress, rely=0, relwidth=1, relheight=1)
                container.update()
                time.sleep(0.001)

        # Run animation
        threading.Thread(target=animate, daemon=True).start()

    def open_about(self):
        """Open the about page with animation"""
        logger.info("Opening about page")
        # Hide the sidebar first
        if self.sidebar.visible:
            self.sidebar.toggle()
        
        # Create container for animation
        container = ctk.CTkFrame(self.main_frame, fg_color="#1a1a1a")
        container.pack(fill="both", expand=True)

        # Create about frame starting from right
        about_frame = ctk.CTkFrame(container, fg_color="#1a1a1a")
        about_frame.place(relx=1.0, rely=0, relwidth=1, relheight=1)

        # Create main frame for animation
        current_frame = ctk.CTkFrame(container, fg_color="#1a1a1a")
        current_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Move existing content to current frame
        for widget in self.main_frame.winfo_children():
            if widget != container:
                widget.pack_forget()
                widget.pack(in_=current_frame, fill="both", expand=True)

        # Add about content
        AboutPage.open(about_frame, lambda: self.transition_to_main(container, about_frame))

        def animate():
            duration = 0.3
            steps = 12
            
            for i in range(steps + 1):
                if not container.winfo_exists():
                    return
                t = i / steps
                t = 1 - (1 - t) * (1 - t)
                
                progress = t
                current_frame.place(relx=-progress, rely=0, relwidth=1, relheight=1)
                about_frame.place(relx=1-progress, rely=0, relwidth=1, relheight=1)
                container.update()
                time.sleep(0.001)

        # Run animation
        threading.Thread(target=animate, daemon=True).start()

    def open_help(self):
        """Open the help page with animation"""
        logger.info("Opening help page")
        # Hide the sidebar first
        if self.sidebar.visible:
            self.sidebar.toggle()
        
        # Create container for animation
        container = ctk.CTkFrame(self.main_frame, fg_color="#1a1a1a")
        container.pack(fill="both", expand=True)

        # Create help frame starting from right
        help_frame = ctk.CTkFrame(container, fg_color="#1a1a1a")
        help_frame.place(relx=1.0, rely=0, relwidth=1, relheight=1)

        # Create main frame for animation
        current_frame = ctk.CTkFrame(container, fg_color="#1a1a1a")
        current_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Move existing content to current frame
        for widget in self.main_frame.winfo_children():
            if widget != container:
                widget.pack_forget()
                widget.pack(in_=current_frame, fill="both", expand=True)

        # Add help content
        HelpPage.open(help_frame, lambda: self.transition_to_main(container, help_frame))

        def animate():
            duration = 0.3
            steps = 12
            
            for i in range(steps + 1):
                if not container.winfo_exists():
                    return
                t = i / steps
                t = 1 - (1 - t) * (1 - t)
                
                progress = t
                current_frame.place(relx=-progress, rely=0, relwidth=1, relheight=1)
                help_frame.place(relx=1-progress, rely=0, relwidth=1, relheight=1)
                container.update()
                time.sleep(0.001)

        # Run animation
        threading.Thread(target=animate, daemon=True).start()

    def open_clip_video(self):
        """Open the clip video page with animation"""
        logger.info("Opening clip video page")
        # Hide the sidebar first
        if self.sidebar.visible:
            self.sidebar.toggle()
        
        # Create container for animation
        container = ctk.CTkFrame(self.main_frame, fg_color="#1a1a1a")
        container.pack(fill="both", expand=True)

        # Create clip video frame starting from right
        clip_frame = ctk.CTkFrame(container, fg_color="#1a1a1a")
        clip_frame.place(relx=1.0, rely=0, relwidth=1, relheight=1)

        # Create main frame for animation
        current_frame = ctk.CTkFrame(container, fg_color="#1a1a1a")
        current_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Move existing content to current frame
        for widget in self.main_frame.winfo_children():
            if widget != container:
                widget.pack_forget()
                widget.pack(in_=current_frame, fill="both", expand=True)

        # Add clip video content
        ClipVideoPage(clip_frame, lambda: self.transition_to_main(container, clip_frame)).pack(fill="both", expand=True)

        def animate():
            duration = 0.3
            steps = 12
            
            for i in range(steps + 1):
                if not container.winfo_exists():
                    return
                t = i / steps
                t = 1 - (1 - t) * (1 - t)
                
                progress = t
                current_frame.place(relx=-progress, rely=0, relwidth=1, relheight=1)
                clip_frame.place(relx=1-progress, rely=0, relwidth=1, relheight=1)
                container.update()
                time.sleep(0.001)

        # Run animation
        threading.Thread(target=animate, daemon=True).start()

    def on_download_complete(self, video_info):
        """Called when a download completes successfully"""
        logger.info("Download complete")
        self.add_notification(f"Download complete: {video_info.get('title', 'Unknown')}", level="success")
        self.update_progress_bar(1.0)
        self.enable_download_button()
        self.reset_progress()

    def on_download_error(self, error):
        """Called when a download fails"""
        logger.error("Download failed")
        self.add_notification(f"Download failed: {str(error)}", level="error")
        self.update_progress_bar(0)
        self.enable_download_button()
        self.reset_progress()

    def load_notifications(self):
        """Load notifications from file"""
        logger.info("Loading notifications")
        try:
            with open(os.path.join(self.app_data_dir, "notifications.json"), "r") as f:
                self.notifications = json.load(f)
                self.unread_notifications = [n for n in self.notifications if not n.get("read", False)]
        except (FileNotFoundError, json.JSONDecodeError):
            self.notifications = []
            self.unread_notifications = []

    def add_notification(self, message, level="info"):
        """Add a new notification"""
        logger.info("Adding notification")
        notification = {
            "message": message,
            "level": level,
            "read": False,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.notifications.append(notification)
        if not notification["read"]:
            self.unread_notifications.append(notification)
        self.update_notification_button()
        self._save_notifications()

    def update_notification_button(self):
        """Update notification button appearance"""
        logger.info("Updating notification button")
        unread_count = len(self.unread_notifications)
        if unread_count > 0:
            self.notification_button.configure(
                text=f"🔔 {unread_count}",
                fg_color="#3b3b3b",
                text_color=("gray10", "gray90")
            )
        else:
            self.notification_button.configure(
                text="🔔",
                fg_color="#2b2b2b",
                text_color=("gray20", "gray80")
            )

    def toggle_notifications(self):
        """Toggle notification popover visibility"""
        logger.info("Toggling notifications")
        
        if not hasattr(self, 'notification_popover'):
            logger.warning("notification_popover not initialized")
            return
            
        logger.info(f"Current popover visibility: {self.notification_popover.visible}")
        
        if self.notification_popover.visible:
            logger.info("Hiding notification popover")
            self.notification_popover.hide()
            self.unbind_all('<Button-1>')  # Remove any existing bindings
        else:
            logger.info("Showing notification popover")
            # Calculate position below notification button
            x = self.notification_button.winfo_rootx()
            y = self.notification_button.winfo_rooty() + self.notification_button.winfo_height() + 5
            logger.debug(f"Positioning popover at x={x}, y={y}")
            
            self.notification_popover.geometry(f"+{x}+{y}")
            self.notification_popover.show()
            self.notification_popover.focus_set()  # Set focus to the popover
            self.unread_notifications = []  # Mark as read
            self.update_notification_button()
            logger.info("Notification popover shown and updated")
            
            # Schedule the click binding for the next event cycle
            self.after(100, self._bind_click_outside)
            
    def _bind_click_outside(self):
        """Bind click outside event after a delay"""
        logger.debug("Binding click outside event")
        self.bind_all('<Button-1>', self._check_click_outside, '+')
            
    def _check_click_outside(self, event):
        """Check if click is outside the notification popover"""
        logger.debug(f"Checking click outside at ({event.x_root}, {event.y_root})")
        
        # Ignore clicks on the notification button
        if event.widget == self.notification_button:
            logger.debug("Click on notification button, ignoring")
            return
            
        # Check if click is inside the popover
        if not self.notification_popover.is_click_inside(event.x_root, event.y_root):
            logger.info("Click detected outside popover")
            self.notification_popover.hide()
            self.unbind_all('<Button-1>')  # Remove the binding after hiding

    def handle_click(self, event):
        """Handle clicks outside notification popover"""
        logger.info("Handling click outside notification popover")
        if self.notification_popover and self.notification_popover.visible:
            if not self.notification_popover.is_click_inside(event.x_root, event.y_root):
                self.notification_popover.hide()

    def _save_notifications(self):
        """Save notifications to file"""
        logger.info("Saving notifications")
        try:
            with open(os.path.join(self.app_data_dir, "notifications.json"), "w") as f:
                json.dump(self.notifications, f)
        except Exception as e:
            logging.error(f"Failed to save notifications: {e}")

    def on_closing(self):
        """Handle window closing event"""
        logger.info("Window closing")
        self.quit()
        
    def start_move(self, event):
        """Start window movement"""
        logger.info("Starting window movement")
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        
    def stop_move(self, event):
        """Stop window movement"""
        logger.info("Stopping window movement")
        self._drag_start_x = None
        self._drag_start_y = None
        
    def do_move(self, event):
        """Handle window movement"""
        logger.info("Moving window")
        if hasattr(self, '_drag_start_x') and self._drag_start_x is not None:
            dx = event.x - self._drag_start_x
            dy = event.y - self._drag_start_y
            x = self.winfo_x() + dx
            y = self.winfo_y() + dy
            self.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    app = YoutubeConverterApp()
    app.mainloop()
