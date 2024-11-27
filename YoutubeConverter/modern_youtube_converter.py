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

        # Configure window
        self.title("Modern YouTube Converter")
        self.geometry("800x600")
        self.minsize(400, 500)
        
        # Set window color
        self._set_appearance_mode("dark")
        self.configure(fg_color=DARKER_COLOR)

        # Create main container
        self.main_container = ctk.CTkFrame(self, fg_color=DARKER_COLOR)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create header frame for hamburger menu
        self.header_frame = ctk.CTkFrame(self.main_container, fg_color=DARKER_COLOR, height=40)
        self.header_frame.pack(fill="x", pady=(0, 10))
        self.header_frame.pack_propagate(False)

        # Add hamburger button
        self.hamburger_button = HamburgerButton(
            self.header_frame,
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

        # Title label
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="YouTube Converter",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=TEXT_COLOR
        )
        self.title_label.pack(pady=(0, 20))

        # Initialize UI components
        self.setup_menu()
        MainPage.open(self.main_frame)

    def setup_menu(self):
        menu_items = [
            ("⚙️", "Settings", self.open_settings),
            ("ℹ️", "About", self.open_about),
            ("❓", "Help", self.open_help)
        ]

        for icon, text, command in menu_items:
            self.sidebar.add_menu_item(icon, text, command)

    def toggle_menu(self):
        self.sidebar.toggle()

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
                if widget == self.title_label:
                    widget.pack(in_=current_frame, pady=(0, 20))
                else:
                    widget.pack(in_=current_frame, fill="both", expand=True)

        # Add settings content
        SettingsPage.open(settings_frame, lambda: self.transition_to_main(container, settings_frame))

        def animate():
            duration = 0.3
            steps = 20
            
            for i in range(steps + 1):
                progress = i / steps
                current_frame.place(relx=-progress, rely=0, relwidth=1, relheight=1)
                settings_frame.place(relx=1-progress, rely=0, relwidth=1, relheight=1)
                container.update()
                time.sleep(duration / steps)

        # Run animation
        threading.Thread(target=animate, daemon=True).start()

    def transition_to_main(self, container, settings_frame):
        """Transition from settings/about/help back to main page"""
        try:
            # Create main frame starting from left
            main_frame = ctk.CTkFrame(container, fg_color=DARKER_COLOR)
            main_frame.place(relx=-1.0, rely=0, relwidth=1, relheight=1)

            # Add title back
            title_label = ctk.CTkLabel(
                main_frame,
                text="YouTube Converter",
                font=ctk.CTkFont(size=28, weight="bold"),
                text_color=TEXT_COLOR
            )
            title_label.pack(pady=(0, 20))

            # Add main page content
            MainPage.open(main_frame)

            def cleanup_widgets(frame):
                """Safely cleanup widgets in a frame"""
                if not frame.winfo_exists():
                    return
                
                # Get all children before starting destruction
                children = list(frame.winfo_children())
                
                # Destroy children first
                for child in children:
                    if hasattr(child, 'winfo_children'):
                        cleanup_widgets(child)
                    if child.winfo_exists():
                        child.destroy()

            def animate():
                try:
                    duration = 0.3
                    steps = 20
                    
                    # Perform the sliding animation
                    for i in range(steps + 1):
                        if not container.winfo_exists():
                            return
                        progress = i / steps
                        settings_frame.place(relx=progress, rely=0, relwidth=1, relheight=1)
                        main_frame.place(relx=-1+progress, rely=0, relwidth=1, relheight=1)
                        container.update()
                        time.sleep(duration / steps)

                    # Wait a brief moment before cleanup
                    container.after(50, lambda: finish_transition())

                except Exception as e:
                    print(f"Animation error: {e}")

            def finish_transition():
                try:
                    if container.winfo_exists():
                        # Safely cleanup all widgets
                        cleanup_widgets(container)
                        container.destroy()

                    # Recreate main content
                    if self.main_frame.winfo_exists():
                        # Clear existing content
                        for widget in self.main_frame.winfo_children():
                            widget.destroy()

                        # Add the title back
                        self.title_label = ctk.CTkLabel(
                            self.main_frame,
                            text="YouTube Converter",
                            font=ctk.CTkFont(size=28, weight="bold"),
                            text_color=TEXT_COLOR
                        )
                        self.title_label.pack(pady=(0, 20))
                        
                        # Restore main page content
                        MainPage.open(self.main_frame)

                except Exception as e:
                    print(f"Transition cleanup error: {e}")

            # Start the animation
            container.after(10, animate)

        except Exception as e:
            print(f"Transition error: {e}")

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
                if widget == self.title_label:
                    widget.pack(in_=current_frame, pady=(0, 20))
                else:
                    widget.pack(in_=current_frame, fill="both", expand=True)

        # Add about content
        AboutPage.open(about_frame, lambda: self.transition_to_main(container, about_frame))

        def animate():
            duration = 0.3
            steps = 20
            
            for i in range(steps + 1):
                progress = i / steps
                current_frame.place(relx=-progress, rely=0, relwidth=1, relheight=1)
                about_frame.place(relx=1-progress, rely=0, relwidth=1, relheight=1)
                container.update()
                time.sleep(duration / steps)

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
                if widget == self.title_label:
                    widget.pack(in_=current_frame, pady=(0, 20))
                else:
                    widget.pack(in_=current_frame, fill="both", expand=True)

        # Add help content
        HelpPage.open(help_frame, lambda: self.transition_to_main(container, help_frame))

        def animate():
            duration = 0.3
            steps = 20
            
            for i in range(steps + 1):
                progress = i / steps
                current_frame.place(relx=-progress, rely=0, relwidth=1, relheight=1)
                help_frame.place(relx=1-progress, rely=0, relwidth=1, relheight=1)
                container.update()
                time.sleep(duration / steps)

        # Run animation
        threading.Thread(target=animate, daemon=True).start()

if __name__ == "__main__":
    app = YoutubeConverterApp()
    app.mainloop()
