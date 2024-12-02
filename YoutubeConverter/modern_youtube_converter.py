import customtkinter as ctk
from PIL import Image
import os
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
from utils.settings_manager import SettingsManager

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
        self.geometry("900x600")  # Increased initial width
        self.minsize(800, 500)  # Set minimum size to prevent UI elements from being cut off
        
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
        
        # Window attributes
        self._focused_widget = None
        
        # Set window color
        self._set_appearance_mode("dark")
        self.configure(fg_color=DARKER_COLOR)

        # Create main container
        self.main_container = ctk.CTkFrame(self, fg_color=DARKER_COLOR)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
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
        button_frame = ctk.CTkFrame(self.header_frame, fg_color=DARKER_COLOR)
        button_frame.pack(side="right", padx=10)

        # Screenshot button
        self.screenshot_button = AnimatedButton(
            button_frame,
            text="📸",
            width=40,
            height=40,
            fg_color=ACCENT_COLOR,
            hover_color=HOVER_COLOR,
            command=self.toggle_screenshot_mode,
            tooltip_text="Take Screenshot (Alt+S)"
        )
        self.screenshot_button.pack(side="right", padx=(20, 0))  # Add padding between buttons

        # Menu toggle button
        self.hamburger_button = HamburgerButton(
            button_frame,
            fg_color=ACCENT_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR,
            command=self.toggle_menu
        )
        self.hamburger_button.pack(side="right")

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
        MainPage.open(self.main_frame)

    def _save_window_state(self):
        """Save current window state"""
        self._window_states['normal_state'] = {
            'topmost': self.attributes('-topmost'),
            'focus': self.focus_get(),
            'alpha': self.attributes('-alpha')
        }

    def _restore_window_state(self):
        """Restore previous window state"""
        state = self._window_states['normal_state']
        self.attributes('-topmost', state['topmost'])
        self.attributes('-alpha', state['alpha'])
        if state['focus'] and state['focus'].winfo_exists():
            state['focus'].focus_set()

    def _on_configure(self, event):
        """Handle window configuration changes"""
        if hasattr(self, 'overlay') and self.overlay.winfo_exists():
            # Update overlay position to match main window
            x = self.winfo_x()
            y = self.winfo_y()
            width = self.winfo_width()
            height = self.winfo_height()
            self.overlay.geometry(f"{width}x{height}+{x}+{y}")

    def _on_focus_in(self, event):
        """Handle window focus in"""
        if self._is_screenshot_mode:
            # Ensure window stays on top and visible
            self.attributes('-alpha', 1.0)
            self.attributes('-topmost', True)
            # Bring overlay to front if it exists
            if hasattr(self, 'overlay') and self.overlay.winfo_exists():
                self.overlay.lift()

    def _on_focus_out(self, event):
        """Handle window focus out"""
        if self._is_screenshot_mode:
            # Keep window visible but slightly transparent when not focused
            self.attributes('-alpha', 0.95)
            self.after(10, lambda: self.attributes('-topmost', True))
            # Ensure overlay stays on top
            if hasattr(self, 'overlay') and self.overlay.winfo_exists():
                self.overlay.lift()
                self.overlay.focus_force()

    def setup_menu(self):
        menu_items = [
            ("⚙️", "Settings", self.open_settings),
            ("📂", "Downloads", self.open_downloads),
            ("🎨", "Themes", self.open_themes),
            ("📊", "Statistics", self.open_statistics),
            ("ℹ️", "About", self.open_about),
            ("❓", "Help", self.open_help)
        ]

        for icon, text, command in menu_items:
            self.sidebar.add_menu_item(icon, text, command)

    def toggle_menu(self):
        self.sidebar.toggle()

    def toggle_screenshot_mode(self, event=None):
        """Toggle screenshot mode"""
        if self._is_screenshot_mode:
            self.exit_screenshot_mode()
        else:
            self.enter_screenshot_mode()

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

    def enter_screenshot_mode(self):
        """Enter screenshot mode"""
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
        if not self._is_screenshot_mode:
            return
            
        self._is_screenshot_mode = False
        self.screenshot_button.configure(fg_color=ACCENT_COLOR)
        
        # Remove overlay
        if hasattr(self, 'overlay') and self.overlay.winfo_exists():
            self.overlay.destroy()
        
        # Restore previous window state
        self._restore_window_state()

    def open_settings(self):
        """Open the settings page"""
        # Hide the sidebar first
        if self.sidebar.visible:
            self.sidebar.toggle()
        
        # Create container for animation
        container = ctk.CTkFrame(self.main_frame, fg_color=DARKER_COLOR)
        container.pack(fill="both", expand=True)

        # Create settings frame starting from right
        settings_frame = ctk.CTkFrame(container, fg_color=DARKER_COLOR)
        settings_frame.place(relx=1.0, rely=0, relwidth=1, relheight=1)

        # Create main frame for animation
        current_frame = ctk.CTkFrame(container, fg_color=DARKER_COLOR)
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
        try:
            if container is None:
                container = self.main_frame
                
            # Create main frame starting from left
            main_frame = ctk.CTkFrame(container, fg_color=DARKER_COLOR)
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
        # Hide the sidebar first
        if self.sidebar.visible:
            self.sidebar.toggle()
        
        # Create container for animation
        container = ctk.CTkFrame(self.main_frame, fg_color=DARKER_COLOR)
        container.pack(fill="both", expand=True)

        # Create downloads frame starting from right
        downloads_frame = ctk.CTkFrame(container, fg_color=DARKER_COLOR)
        downloads_frame.place(relx=1.0, rely=0, relwidth=1, relheight=1)

        # Create main frame for animation
        current_frame = ctk.CTkFrame(container, fg_color=DARKER_COLOR)
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
        # Hide the sidebar first
        if self.sidebar.visible:
            self.sidebar.toggle()
        
        # Create container for animation
        container = ctk.CTkFrame(self.main_frame, fg_color=DARKER_COLOR)
        container.pack(fill="both", expand=True)

        # Create themes frame starting from right
        themes_frame = ctk.CTkFrame(container, fg_color=DARKER_COLOR)
        themes_frame.place(relx=1.0, rely=0, relwidth=1, relheight=1)

        # Create main frame for animation
        current_frame = ctk.CTkFrame(container, fg_color=DARKER_COLOR)
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
        # Hide the sidebar first
        if self.sidebar.visible:
            self.sidebar.toggle()
        
        # Create container for animation
        container = ctk.CTkFrame(self.main_frame, fg_color=DARKER_COLOR)
        container.pack(fill="both", expand=True)

        # Create statistics frame starting from right
        statistics_frame = ctk.CTkFrame(container, fg_color=DARKER_COLOR)
        statistics_frame.place(relx=1.0, rely=0, relwidth=1, relheight=1)

        # Create main frame for animation
        current_frame = ctk.CTkFrame(container, fg_color=DARKER_COLOR)
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
        # Hide the sidebar first
        if self.sidebar.visible:
            self.sidebar.toggle()
        
        # Create container for animation
        container = ctk.CTkFrame(self.main_frame, fg_color=DARKER_COLOR)
        container.pack(fill="both", expand=True)

        # Create about frame starting from right
        about_frame = ctk.CTkFrame(container, fg_color=DARKER_COLOR)
        about_frame.place(relx=1.0, rely=0, relwidth=1, relheight=1)

        # Create main frame for animation
        current_frame = ctk.CTkFrame(container, fg_color=DARKER_COLOR)
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
        # Hide the sidebar first
        if self.sidebar.visible:
            self.sidebar.toggle()
        
        # Create container for animation
        container = ctk.CTkFrame(self.main_frame, fg_color=DARKER_COLOR)
        container.pack(fill="both", expand=True)

        # Create help frame starting from right
        help_frame = ctk.CTkFrame(container, fg_color=DARKER_COLOR)
        help_frame.place(relx=1.0, rely=0, relwidth=1, relheight=1)

        # Create main frame for animation
        current_frame = ctk.CTkFrame(container, fg_color=DARKER_COLOR)
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

if __name__ == "__main__":
    app = YoutubeConverterApp()
    app.mainloop()
