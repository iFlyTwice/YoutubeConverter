import customtkinter as ctk
from tkinter import filedialog
import os
import json
from .notification_popup import NotificationPopup
from .custom_dropdown import CustomDropdown
from utils.settings_manager import SettingsManager
from utils.event_manager import EventManager
from threads.settings_page_thread import SettingsPageThread
import threading
import time
import logging

logger = logging.getLogger(__name__)

DARKER_COLOR = "#1a1a1a"
ACCENT_COLOR = "#333333"
HOVER_COLOR = "#404040"
TEXT_COLOR = "#ffffff"
CORNER_RADIUS = 8

class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, app=None, on_back_click=None, **kwargs):
        # Store parameters before super().__init__
        self.app = app
        self.on_back_click = on_back_click
        # Remove app and on_back_click from kwargs
        kwargs.pop('app', None)
        kwargs.pop('on_back_click', None)
        super().__init__(master, **kwargs)
        # Initialize managers
        self.settings_manager = SettingsManager()
        self.event_manager = EventManager()
        
        # Initialize thread
        self.thread = SettingsPageThread()
        self.thread.register_callback("load_settings", self.load_settings)
        self.thread.start()
        
        # Track settings state
        self.settings_changed = False
        self.initial_settings = {}
        self.current_settings = {}
        self.controls = {}
        
        # Configure the frame
        self.configure(fg_color=DARKER_COLOR)
        
        # Create header with back button
        self.header = ctk.CTkFrame(self, fg_color="#232323", height=50)
        self.header.pack(fill="x", padx=10, pady=10)
        
        # Back button
        self.back_button = ctk.CTkButton(
            self.header,
            text="←",
            width=30,
            command=self.handle_back,
            fg_color="transparent",
            hover_color="#404040"
        )
        self.back_button.pack(side="left", padx=10)
        
        # Title
        self.title = ctk.CTkLabel(
            self.header,
            text="Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title.pack(side="left", padx=10)
        
        # Create scrollable content
        self.content = ctk.CTkScrollableFrame(self)
        self.content.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Add settings sections
        self.add_settings_sections()
        
        self.load_initial_settings()

    def add_settings_sections(self):
        """Add all settings sections to the page"""
        logger.debug("Adding settings sections")
        try:
            # Download Settings
            self.add_section_header("Download Settings")
            
            # Download Location
            download_frame = ctk.CTkFrame(self.content, fg_color="#232323", height=70, corner_radius=CORNER_RADIUS)
            download_frame.pack(fill="x", pady=5)
            download_frame.pack_propagate(False)
            
            # Text container
            text_frame = ctk.CTkFrame(download_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
            
            title_label = ctk.CTkLabel(
                text_frame,
                text="Download Location",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=TEXT_COLOR
            )
            title_label.pack(anchor="w")
            
            desc_label = ctk.CTkLabel(
                text_frame,
                text="Choose where to save downloaded files",
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color="#888888"
            )
            desc_label.pack(anchor="w")
            
            # Download path entry and browse button container
            path_frame = ctk.CTkFrame(download_frame, fg_color="transparent")
            path_frame.pack(side="right", fill="y", padx=15)
            
            download_path_entry = ctk.CTkEntry(
                path_frame,
                width=200,
                height=32,
                font=ctk.CTkFont(family="Segoe UI", size=12)
            )
            download_path_entry.pack(side="left", padx=(0, 5))
            self.controls['download_path'] = download_path_entry
            
            browse_btn = ctk.CTkButton(
                path_frame,
                text="Browse",
                width=70,
                height=32,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                command=lambda: self.browse_folder(download_path_entry)
            )
            browse_btn.pack(side="left")
            
            # Default Format
            format_frame = ctk.CTkFrame(self.content, fg_color="#232323", height=70, corner_radius=CORNER_RADIUS)
            format_frame.pack(fill="x", pady=5)
            format_frame.pack_propagate(False)
            
            # Text container
            text_frame = ctk.CTkFrame(format_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
            
            title_label = ctk.CTkLabel(
                text_frame,
                text="Default Format",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=TEXT_COLOR
            )
            title_label.pack(anchor="w")
            
            desc_label = ctk.CTkLabel(
                text_frame,
                text="Choose the default download format",
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color="#888888"
            )
            desc_label.pack(anchor="w")
            
            format_dropdown = CustomDropdown(
                format_frame,
                values=["MP4", "MP3"],
                width=100,
                command=lambda _: self.on_setting_changed()
            )
            format_dropdown.pack(side="right", padx=15)
            self.controls['default_format'] = format_dropdown
            
            # Video Quality
            quality_frame = ctk.CTkFrame(self.content, fg_color="#232323", height=70, corner_radius=CORNER_RADIUS)
            quality_frame.pack(fill="x", pady=5)
            quality_frame.pack_propagate(False)
            
            # Text container
            text_frame = ctk.CTkFrame(quality_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
            
            title_label = ctk.CTkLabel(
                text_frame,
                text="Video Quality",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=TEXT_COLOR
            )
            title_label.pack(anchor="w")
            
            desc_label = ctk.CTkLabel(
                text_frame,
                text="Select preferred video quality",
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color="#888888"
            )
            desc_label.pack(anchor="w")
            
            quality_dropdown = CustomDropdown(
                quality_frame,
                values=["Highest", "1080p", "720p", "480p", "360p"],
                width=100,
                command=lambda _: self.on_setting_changed()
            )
            quality_dropdown.pack(side="right", padx=15)
            self.controls['video_quality'] = quality_dropdown
            
            # Audio Settings
            self.add_section_header("Audio Settings")
            
            # Audio Format
            audio_format_frame = ctk.CTkFrame(self.content, fg_color="#232323", height=70, corner_radius=CORNER_RADIUS)
            audio_format_frame.pack(fill="x", pady=5)
            audio_format_frame.pack_propagate(False)
            
            text_frame = ctk.CTkFrame(audio_format_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
            
            title_label = ctk.CTkLabel(
                text_frame,
                text="Audio Format",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=TEXT_COLOR
            )
            title_label.pack(anchor="w")
            
            desc_label = ctk.CTkLabel(
                text_frame,
                text="Choose audio format for extraction",
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color="#888888"
            )
            desc_label.pack(anchor="w")
            
            audio_format_dropdown = CustomDropdown(
                audio_format_frame,
                values=["MP3", "WAV", "AAC", "M4A"],
                width=120,
                height=32,
                command=lambda value: self.on_setting_changed("audio_format", value)
            )
            audio_format_dropdown.pack(side="right", padx=15, pady=10)
            self.controls['audio_format'] = audio_format_dropdown
            
            # Audio Quality
            audio_quality_frame = ctk.CTkFrame(self.content, fg_color="#232323", height=70, corner_radius=CORNER_RADIUS)
            audio_quality_frame.pack(fill="x", pady=5)
            audio_quality_frame.pack_propagate(False)
            
            text_frame = ctk.CTkFrame(audio_quality_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
            
            title_label = ctk.CTkLabel(
                text_frame,
                text="Audio Quality",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=TEXT_COLOR
            )
            title_label.pack(anchor="w")
            
            desc_label = ctk.CTkLabel(
                text_frame,
                text="Select audio bitrate",
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color="#888888"
            )
            desc_label.pack(anchor="w")
            
            audio_quality_dropdown = CustomDropdown(
                audio_quality_frame,
                values=["320kbps", "256kbps", "192kbps", "128kbps"],
                width=120,
                height=32,
                command=lambda value: self.on_setting_changed("audio_quality", value)
            )
            audio_quality_dropdown.pack(side="right", padx=15, pady=10)
            self.controls['audio_quality'] = audio_quality_dropdown
            
            # Application Settings
            self.add_section_header("Application Settings")
            
            # Always on Top
            always_on_top_frame = ctk.CTkFrame(self.content, fg_color="#232323", height=70, corner_radius=CORNER_RADIUS)
            always_on_top_frame.pack(fill="x", pady=5)
            always_on_top_frame.pack_propagate(False)
            
            text_frame = ctk.CTkFrame(always_on_top_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
            
            title_label = ctk.CTkLabel(
                text_frame,
                text="Always on Top",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=TEXT_COLOR
            )
            title_label.pack(anchor="w")
            
            desc_label = ctk.CTkLabel(
                text_frame,
                text="Keep window on top of other windows",
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color="#888888"
            )
            desc_label.pack(anchor="w")
            
            always_on_top_switch = ctk.CTkSwitch(
                always_on_top_frame,
                text="",
                width=46,
                height=24,
                fg_color=ACCENT_COLOR,
                progress_color="#4CAF50",
                button_color=TEXT_COLOR,
                button_hover_color="#f0f0f0",
                command=lambda: self.on_setting_changed("always_on_top")
            )
            always_on_top_switch.pack(side="right", padx=15, pady=10)
            self.controls['always_on_top'] = always_on_top_switch
            
        except Exception as e:
            logger.error(f"Error in add_settings_sections: {str(e)}")
            raise

    def add_section_header(self, text):
        """Add a section header with consistent styling"""
        # Add spacing before section (except first section)
        if self.content.winfo_children():
            spacer = ctk.CTkFrame(self.content, fg_color="transparent", height=20)
            spacer.pack(fill="x")
        
        # Section header
        header_frame = ctk.CTkFrame(self.content, fg_color="transparent", height=40)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        label = ctk.CTkLabel(
            header_frame,
            text=text,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=TEXT_COLOR
        )
        label.pack(side="left")
        
        # Separator
        separator = ctk.CTkFrame(self.content, fg_color=ACCENT_COLOR, height=1)
        separator.pack(fill="x", pady=(5, 10))

    def load_settings(self):
        """Load settings from the settings manager"""
        try:
            settings = self.settings_manager.load_settings()
            self.update_ui_with_settings(settings)
            return settings
        except Exception as e:
            logger.error(f"Error loading settings: {str(e)}")
            return None

    def update_ui_with_settings(self, settings):
        """Update UI elements with loaded settings"""
        if not settings:
            return
            
        # Update download path if available
        if 'download_path' in settings:
            self.controls['download_path'].delete(0, 'end')
            self.controls['download_path'].insert(0, settings['download_path'])
            
        # Update quality selection if available
        if 'video_quality' in settings:
            self.controls['video_quality'].set(settings['video_quality'])
            
        # Update format selection if available
        if 'default_format' in settings:
            self.controls['default_format'].set(settings['default_format'])
            
        # Update audio format selection if available
        if 'audio_format' in settings:
            self.controls['audio_format'].set(settings['audio_format'])
            
        # Update audio quality selection if available
        if 'audio_quality' in settings:
            self.controls['audio_quality'].set(settings['audio_quality'])
            
        # Update always on top switch if available
        if 'always_on_top' in settings:
            if settings['always_on_top']:
                self.controls['always_on_top'].select()
            else:
                self.controls['always_on_top'].deselect()

    def load_initial_settings(self):
        """Load initial settings in a background thread"""
        self.thread.add_task(("load_settings", None))

    def save_settings(self):
        """Save the current settings"""
        try:
            # Get current settings from controls
            current_settings = {}
            for key, control in self.controls.items():
                if isinstance(control, ctk.CTkSwitch):
                    current_settings[key] = bool(control.get())
                elif isinstance(control, ctk.CTkEntry):
                    current_settings[key] = control.get()
                elif isinstance(control, CustomDropdown):
                    current_settings[key] = control.get()
            
            # Save settings in background thread
            self.thread.add_task(("save_settings", current_settings))
            
            # Update initial settings to match current
            self.initial_settings = current_settings.copy()
            self.settings_changed = False
            
            # Emit settings updated event
            self.event_manager.emit("settings_updated", self.initial_settings)
            
            # Clean up settings page
            self.cleanup()
            
            # Hide settings page
            self.pack_forget()
            
            # Create and show main page
            app = self.winfo_toplevel()
            main_frame = app.main_frame
            
            # Clear main frame
            for widget in main_frame.winfo_children():
                widget.destroy()
            
            # Create new main page
            from components.main_page import MainPage
            main_page = MainPage(main_frame, fg_color=DARKER_COLOR)
            main_page.pack(fill="both", expand=True)
            
            # Destroy settings page
            self.destroy()
            
            logger.debug("Settings saved and transitioned to main page")
            return True
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return False

    def handle_save(self):
        """Handle save button click"""
        try:
            if self.save_settings():
                # Show success notification
                NotificationPopup.show_notification(
                    self,
                    "Success",
                    "Settings saved successfully",
                    duration=2
                )
                # Return to main page
                self.transition_to_main()
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            NotificationPopup.show_notification(
                self,
                "Error",
                "Failed to save settings",
                duration=2
            )

    def handle_back(self):
        """Handle back button click"""
        if self.settings_changed:
            # Show confirmation dialog
            dialog = NotificationPopup.show_notification(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before leaving?",
                primary_button="Save",
                secondary_button="Discard"
            )
            
            def check_dialog_result():
                if hasattr(dialog, 'result'):
                    if dialog.result:  # Save
                        if self.save_settings():
                            # Show success notification
                            NotificationPopup.show_notification(
                                self,
                                "Success",
                                "Settings saved successfully",
                                duration=2
                            )
                            self.transition_to_main()
                    elif dialog.result is False:  # Discard
                        self.discard_changes()
                        self.transition_to_main()
            
            # Monitor dialog result
            self.after(100, check_dialog_result)
        else:
            # No changes, just go back
            self.transition_to_main()

    def transition_to_main(self):
        """Clean transition to main page"""
        try:
            # Clean up resources
            self.cleanup()
            
            # Get main app and transition to main page
            app = self.winfo_toplevel()
            app.show_main_page()
            
            # Destroy settings page
            self.destroy()
            
        except Exception as e:
            logger.error(f"Error transitioning to main: {e}")

    def discard_changes(self):
        """Discard changes and restore original settings"""
        try:
            # Restore controls to initial values
            for key, value in self.initial_settings.items():
                if key in self.controls:
                    control = self.controls[key]
                    if isinstance(control, ctk.CTkSwitch):
                        control.select() if value else control.deselect()
                    elif isinstance(control, ctk.CTkEntry):
                        control.delete(0, 'end')
                        control.insert(0, value)
                    elif isinstance(control, CustomDropdown):
                        control.set(value)
            
            self.settings_changed = False
            logger.debug("Settings discarded and restored to initial state")
            
        except Exception as e:
            logger.error(f"Error discarding changes: {e}")

    def on_setting_changed(self, *args):
        """Called when any setting is changed"""
        try:
            # Get current values
            current = {}
            for key, control in self.controls.items():
                if isinstance(control, ctk.CTkSwitch):
                    current[key] = bool(control.get())
                elif isinstance(control, ctk.CTkEntry):
                    current[key] = control.get()
                elif isinstance(control, CustomDropdown):
                    current[key] = control.get()
            
            # Compare with initial settings
            self.settings_changed = current != self.initial_settings
            
            # Update save button state
            # self.save_button.configure(
            #     state="normal" if self.settings_changed else "disabled"
            # )
            
            logger.debug(f"Settings changed: {self.settings_changed}")
            
        except Exception as e:
            logger.error(f"Error checking settings changes: {e}")

    def browse_folder(self, entry):
        """Open folder browser dialog and update entry"""
        folder = filedialog.askdirectory()
        if folder:
            entry.delete(0, 'end')
            entry.insert(0, folder)
            self.on_setting_changed()

    def cleanup(self):
        """Clean up resources before destroying"""
        try:
            # Stop and cleanup thread
            if hasattr(self, 'thread') and self.thread:
                self.thread.stop()
                self.thread.join(timeout=1.0)  # Wait up to 1 second for thread to stop
                logger.debug("Settings page thread stopped")
        except Exception as e:
            logger.error(f"Error cleaning up settings page: {e}")

    def destroy(self):
        """Clean up before destroying"""
        try:
            self.cleanup()
            super().destroy()
        except Exception as e:
            logger.error(f"Error destroying settings page: {e}")

    @staticmethod
    def open(parent_frame, on_back):
        """Open the settings page"""
        settings_frame = SettingsPage(parent_frame)
        settings_frame.pack(fill="both", expand=True)
        return settings_frame
