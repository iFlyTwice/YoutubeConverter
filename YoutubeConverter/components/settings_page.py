import customtkinter as ctk
import threading
import time
from utils.settings_manager import SettingsManager

DARKER_COLOR = "#1a1a1a"
ACCENT_COLOR = "#333333"
HOVER_COLOR = "#404040"
TEXT_COLOR = "#ffffff"

class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, on_back=None, **kwargs):
        super().__init__(master, **kwargs)
        
        # Initialize settings manager
        self.settings_manager = SettingsManager()
        
        self.on_back = on_back
        self.settings_changed = False
        self.initial_settings = {}
        
        # Store control references
        self.controls = {}
        
        # Configure the frame
        self.configure(fg_color="#1a1a1a", corner_radius=12)
        
        # Create header
        self.header = ctk.CTkFrame(self, fg_color="#232323", height=50, corner_radius=8)
        self.header.pack(fill="x", padx=10, pady=10)
        self.header.pack_propagate(False)
        
        # Back button
        self.back_button = ctk.CTkButton(
            self.header,
            text="←",
            width=30,
            fg_color="transparent",
            hover_color="#3d3d3d",
            corner_radius=8,
            command=self.handle_back
        )
        self.back_button.pack(side="left", padx=10)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.header,
            text="Settings",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#ffffff"
        )
        self.title_label.pack(side="left", padx=10)
        
        # Close button
        self.close_button = ctk.CTkButton(
            self.header,
            text="×",
            width=30,
            fg_color="transparent",
            hover_color="#3d3d3d",
            corner_radius=8,
            command=self.handle_back
        )
        self.close_button.pack(side="right", padx=10)
        
        # Create scrollable content
        self.content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Add settings sections
        self.add_settings_sections()
        
        # Now that all controls are created, store initial settings
        self.save_initial_settings()

    def save_initial_settings(self):
        """Store the initial settings state"""
        self.initial_settings = self.settings_manager.load_settings()
        
        # Update controls with saved values
        for key, value in self.initial_settings.items():
            if key in self.controls:
                control = self.controls[key]
                if isinstance(control, ctk.CTkSwitch):
                    if value:
                        control.select()
                    else:
                        control.deselect()
                elif isinstance(control, ctk.CTkEntry):
                    control.delete(0, 'end')
                    control.insert(0, value)
                else:  # OptionMenu
                    control.set(value)
        
        self.settings_changed = False
    
    def check_settings_changed(self):
        """Check if any settings have been modified"""
        current_settings = {}
        for key, control in self.controls.items():
            if isinstance(control, ctk.CTkSwitch):
                current_settings[key] = control.get()
            elif isinstance(control, ctk.CTkEntry):
                current_settings[key] = control.get()
            else:  # OptionMenu
                current_settings[key] = control.get()
        return current_settings != self.initial_settings
    
    def save_settings(self):
        """Save the current settings"""
        current_settings = {}
        for key, control in self.controls.items():
            if isinstance(control, ctk.CTkSwitch):
                current_settings[key] = bool(control.get())
            elif isinstance(control, ctk.CTkEntry):
                current_settings[key] = control.get()
            else:  # OptionMenu
                current_settings[key] = control.get()
        
        # Save to file
        if self.settings_manager.update_settings(current_settings):
            self.initial_settings = current_settings.copy()
            self.settings_changed = False
            return True
        return False
    
    def handle_back(self):
        """Handle back button click"""
        if self.check_settings_changed():
            from .notification_popup import NotificationPopup
            result = NotificationPopup.show_notification(
                self,
                title="Unsaved Changes",
                message="You have unsaved changes. Do you want to save before leaving?",
                primary_button="Save",
                secondary_button="Discard"
            )
            if result:
                if self.save_settings():
                    if self.on_back:
                        self.on_back()
                else:
                    # Show error notification
                    NotificationPopup.show_notification(
                        self,
                        title="Error",
                        message="Failed to save settings. Please try again.",
                        primary_button="OK",
                        secondary_button=""
                    )
            elif result is False:  # User clicked "Discard"
                if self.on_back:
                    self.on_back()
        else:
            if self.on_back:
                self.on_back()

    def on_setting_changed(self, *args):
        """Called when any setting is changed"""
        self.settings_changed = self.check_settings_changed()

    def add_settings_sections(self):
        # Download Settings Section
        self.add_section_title("Download Settings")
        
        # Output Directory
        self.add_setting_item(
            "Output Directory",
            "Choose where to save downloaded videos",
            "folder"
        )
        
        # Video Quality
        self.add_setting_item(
            "Video Quality",
            "Select preferred video quality",
            "dropdown",
            options=["Highest", "1080p", "720p", "480p", "360p"]
        )
        
        # Audio Settings Section
        self.add_section_title("Audio Settings")
        
        # Audio Format
        self.add_setting_item(
            "Audio Format",
            "Choose audio format for extraction",
            "dropdown",
            options=["MP3", "WAV", "AAC", "M4A"]
        )
        
        # Audio Quality
        self.add_setting_item(
            "Audio Quality",
            "Select audio bitrate",
            "dropdown",
            options=["320kbps", "256kbps", "192kbps", "128kbps"]
        )
        
        # Appearance Section
        self.add_section_title("Appearance")
        
        # Theme
        self.add_setting_item(
            "Theme",
            "Choose application theme",
            "dropdown",
            options=["Dark", "Light", "System"]
        )

        # Window Settings
        self.add_section_title("Window Settings")
        
        # Always on Top
        frame = self.create_always_on_top_switch()
        self.add_setting_row(
            "Always on Top",
            "Keep window on top of other windows (Press Alt+T to toggle quickly)",
            frame
        )

    def add_section_title(self, text):
        """Add a section title to the settings"""
        frame = ctk.CTkFrame(self.content, fg_color="transparent", height=50)
        frame.pack(fill="x", pady=(20, 10))
        frame.pack_propagate(False)
        
        label = ctk.CTkLabel(
            frame,
            text=text,
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#ffffff"
        )
        label.pack(side="left")
        
        # Add separator
        separator = ctk.CTkFrame(self.content, fg_color="#333333", height=1)
        separator.pack(fill="x", pady=(0, 10))

    def add_setting_item(self, title, description, type_, **kwargs):
        """Add a setting item with title, description and appropriate control"""
        frame = ctk.CTkFrame(self.content, fg_color="#232323", height=70, corner_radius=8)
        frame.pack(fill="x", pady=5)
        frame.pack_propagate(False)
        
        # Text container
        text_frame = ctk.CTkFrame(frame, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            text_frame,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#ffffff"
        )
        title_label.pack(anchor="w")
        
        # Description
        desc_label = ctk.CTkLabel(
            text_frame,
            text=description,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#888888"
        )
        desc_label.pack(anchor="w")
        
        # Control
        control_id = title.lower().replace(" ", "_")
        
        if type_ == "dropdown":
            control = ctk.CTkOptionMenu(
                frame,
                values=kwargs.get("options", []),
                fg_color="#333333",
                button_color="#404040",
                button_hover_color="#4d4d4d",
                width=120,
                command=self.on_setting_changed
            )
            control.pack(side="right", padx=15)
            self.controls[control_id] = control
            
        elif type_ == "folder":
            entry = ctk.CTkEntry(
                frame,
                width=200,
                height=30,
                corner_radius=8,
                fg_color="#333333",
                text_color="#ffffff",
                placeholder_text="Select folder"
            )
            entry.pack(side="right", padx=(0, 10))
            self.controls[control_id] = entry
            
            browse_button = ctk.CTkButton(
                frame,
                text="Browse",
                fg_color="#333333",
                hover_color="#404040",
                width=80,
                command=lambda e=entry: self.browse_folder(e)
            )
            browse_button.pack(side="right", padx=5)

    def add_setting_row(self, title, description, control):
        """Add a setting row with title, description and control"""
        frame = ctk.CTkFrame(self.content, fg_color="#232323", height=70, corner_radius=8)
        frame.pack(fill="x", pady=5)
        frame.pack_propagate(False)
        
        # Text container
        text_frame = ctk.CTkFrame(frame, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            text_frame,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#ffffff"
        )
        title_label.pack(anchor="w")
        
        # Description
        desc_label = ctk.CTkLabel(
            text_frame,
            text=description,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#888888"
        )
        desc_label.pack(anchor="w")
        
        # Control container
        control_frame = ctk.CTkFrame(frame, fg_color="transparent", width=60)
        control_frame.pack(side="right", padx=15, pady=10)
        control_frame.pack_propagate(False)
        
        # Center the control in its frame
        control.pack(in_=control_frame, expand=True)
        
        return frame

    def create_always_on_top_switch(self):
        """Create the always on top switch"""
        switch = ctk.CTkSwitch(
            self.content,
            text="",
            fg_color=ACCENT_COLOR,
            progress_color="#4CAF50",
            button_color="#ffffff",
            button_hover_color="#f0f0f0",
            width=46,
            height=24
        )
        
        # Set initial state
        if self.settings_manager.get_setting('always_on_top'):
            switch.select()
        else:
            switch.deselect()
        
        # Add change callback
        def on_switch_change():
            self.settings_manager.update_setting('always_on_top', switch.get())
            # Update window state
            if self.winfo_toplevel():
                self.winfo_toplevel().attributes('-topmost', switch.get())
            self.settings_changed = True
            
        switch.configure(command=on_switch_change)
        self.controls['always_on_top'] = switch
        return switch

    def browse_folder(self, entry):
        """Open folder browser dialog and update entry"""
        import tkinter.filedialog as filedialog
        folder = filedialog.askdirectory()
        if folder:
            entry.delete(0, 'end')
            entry.insert(0, folder)
            self.on_setting_changed()
    
    @staticmethod
    def open(parent_frame, on_back):
        """Open the settings page"""
        settings_frame = SettingsPage(parent_frame, on_back=on_back)
        settings_frame.pack(fill="both", expand=True)
        return settings_frame
