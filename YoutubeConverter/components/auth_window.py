import customtkinter as ctk
import os
from pathlib import Path
import threading
import json
from YoutubeConverter.utils.cookie_manager import CookieManager
from YoutubeConverter.utils.browser_automation import BrowserAutomation
from YoutubeConverter.utils.ui_helper import UIHelper

class AuthWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = UIHelper()
        self.setup_window()
        self.cookie_manager = CookieManager()
        self.check_auth_status()
        
    def setup_window(self):
        """Setup the authentication window"""
        self.title("YouTube Authentication")
        self.geometry("300x400")
        
        # Center the window
        self.ui.center_window(self, 300, 400)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create widgets
        self.setup_widgets()
        
    def setup_widgets(self):
        """Create and setup all widgets"""
        # Title
        self.title_label = self.ui.create_title_label(
            self,
            text="YouTube Authentication",
            row=0,
            column=0,
            pady=(20, 10),
            padx=20
        )
        
        # Status frame
        self.status_frame = self.ui.create_frame(
            self,
            row=1,
            column=0,
            pady=10,
            padx=20,
            sticky="nsew"
        )
        self.status_frame.grid_columnconfigure(0, weight=1)
        
        # Status indicators
        self.cookie_status = self.create_status_indicator("Cookies", 0)
        self.visitor_status = self.create_status_indicator("Visitor Data", 1)
        
        # Auth button
        self.auth_button = self.ui.create_button(
            self,
            text="Authenticate",
            command=self.start_auth,
            row=2,
            column=0,
            pady=(10, 20),
            padx=20,
            height=40
        )
        
        # Progress bar (hidden by default)
        self.progress = self.ui.create_progress_bar(
            self,
            row=3,
            column=0,
            pady=(0, 20),
            padx=20
        )
        self.progress.set(0)
        self.progress.grid_remove()
        
    def create_status_indicator(self, text, row):
        """Create a status indicator with icon and label"""
        frame = self.ui.create_frame(
            self.status_frame,
            row=row,
            column=0,
            pady=10,
            padx=10,
            fg_color="transparent"
        )
        frame.grid_columnconfigure(1, weight=1)
        
        icon = self.ui.create_label(
            frame,
            text="❌",
            font=("Roboto", 16),
            width=30,
            row=0,
            column=0,
            padx=(10, 5)
        )
        
        label = self.ui.create_label(
            frame,
            text=text,
            font=("Roboto", 14),
            anchor="w",
            row=0,
            column=1,
            sticky="w"
        )
        
        return {"icon": icon, "label": label}
        
    def check_auth_status(self):
        """Check if authentication data exists"""
        has_cookies = self.cookie_manager.has_valid_cookies()
        has_visitor = self.cookie_manager.has_valid_visitor_data()
        
        self.update_status(self.cookie_status, has_cookies)
        self.update_status(self.visitor_status, has_visitor)
        
        if has_cookies and has_visitor:
            self.auth_button.configure(state="disabled", text="Authenticated")
            
    def update_status(self, status_dict, is_valid):
        """Update status indicator"""
        status_dict["icon"].configure(
            text="✓" if is_valid else "❌",
            text_color="green" if is_valid else "red"
        )
        
    def start_auth(self):
        """Start the authentication process"""
        self.auth_button.configure(state="disabled", text="Authenticating...")
        self.progress.grid()
        self.progress.start()
        
        # Run authentication in a separate thread
        thread = threading.Thread(target=self.run_auth)
        thread.daemon = True
        thread.start()
        
    def run_auth(self):
        """Run the authentication process"""
        try:
            automation = BrowserAutomation()
            cookies, visitor_data = automation.get_youtube_auth()
            
            if cookies and visitor_data:
                self.cookie_manager.save_cookies(cookies)
                self.cookie_manager.save_visitor_data(visitor_data)
                
                # Create auth flag file
                flag_path = Path(self.cookie_manager.data_dir) / "auth.flag"
                with open(flag_path, "w") as f:
                    json.dump({
                        "authenticated": True,
                        "timestamp": str(Path(self.cookie_manager.cookie_file).stat().st_mtime)
                    }, f)
                
                # Update UI
                self.after(0, self.auth_success)
            else:
                self.after(0, self.auth_failed)
                
        except Exception as e:
            self.after(0, lambda: self.auth_failed(str(e)))
            
    def auth_success(self):
        """Handle successful authentication"""
        self.progress.stop()
        self.progress.grid_remove()
        self.check_auth_status()
        self.after(2000, self.destroy)  # Close window after 2 seconds
        
    def auth_failed(self, error_msg="Authentication failed"):
        """Handle failed authentication"""
        self.progress.stop()
        self.progress.grid_remove()
        self.auth_button.configure(state="normal", text="Try Again")
        
        # Show error message
        error_label = self.ui.create_label(
            self,
            text=error_msg,
            text_color="red",
            wraplength=260,
            row=4,
            column=0,
            pady=(0, 20),
            padx=20
        )
        self.after(3000, error_label.destroy)  # Remove error after 3 seconds
