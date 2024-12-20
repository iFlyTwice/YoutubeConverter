import customtkinter as ctk
import os
import json
from datetime import datetime
from utils.ui_helper import UIHelper

DARKER_COLOR = "#1a1a1a"
ACCENT_COLOR = "#333333"
HOVER_COLOR = "#404040"
TEXT_COLOR = "#ffffff"

class DownloadsPage(ctk.CTkFrame):
    def __init__(self, master, app, on_back_click=None, **kwargs):
        super().__init__(master, **kwargs)
        
        # Store callback
        self.on_back_click = on_back_click
        self.app = app
        
        # Configure the frame
        self.configure(fg_color="#1a1a1a", corner_radius=12)
        
        # Create header
        self.header = UIHelper.create_section_frame(
            self,
            height=60,
            fg_color="#232323",
            corner_radius=12
        )
        self.header.pack(fill="x", padx=15, pady=(15, 0))
        
        # Add back button with arrow
        self.back_button = UIHelper.create_button(
            self.header,
            text="←",
            command=self.handle_back_click,
            width=40,
            height=40,
            font=("Segoe UI", 20),
            fg_color="transparent",
            hover_color="#3d3d3d"
        )
        self.back_button.pack(side="left", padx=10)
        
        # Add title to header
        title = ctk.CTkLabel(
            self.header,
            text="Downloads",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#ffffff"
        )
        title.pack(side="left", padx=(5, 20))
        
        # Add search frame
        search_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        search_frame.pack(side="left", fill="x", expand=True, padx=10)
        
        # Add search entry
        self.search_entry = UIHelper.create_entry(
            search_frame,
            placeholder_text="Search downloads...",
            width=300,
            height=35,
            font=("Segoe UI", 13),
            fg_color="#1e1e1e",
            border_color="#2d2d2d"
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        
        # Add clear search button
        self.clear_button = UIHelper.create_button(
            search_frame,
            text="×",
            command=self.clear_search,
            width=35,
            height=35,
            font=("Segoe UI", 16),
            fg_color="#1e1e1e",
            hover_color="#2d2d2d"
        )
        # Initially hide the clear button
        self.clear_button.pack_forget()
        
        # Bind search entry to update results and toggle clear button
        self.search_entry.bind("<KeyRelease>", self.on_search_change)
        
        # Add open folder button
        self.folder_button = UIHelper.create_button(
            self.header,
            text="📂 Open Folder",
            command=self.open_downloads_folder,
            font=("Segoe UI", 14),
            fg_color=ACCENT_COLOR,
            hover_color=HOVER_COLOR
        )
        self.folder_button.pack(side="right", padx=10)
        
        # Create content area with scrollable frame
        self.content = ctk.CTkScrollableFrame(
            self,
            fg_color="#1a1a1a",
            corner_radius=0
        )
        self.content.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Add downloads content
        self.add_downloads_sections()
    
    def add_section_title(self, text):
        """Add a section title to the downloads page"""
        frame = UIHelper.create_section_frame(
            self.content,
            height=50,
            fg_color="transparent"
        )
        frame.pack(fill="x", pady=(20, 10))
        
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

    def add_download_item(self, download):
        """Add a download item to the list"""
        frame = UIHelper.create_section_frame(
            self.content,
            fg_color="#232323"
        )
        frame.pack(fill="x", pady=5)
        
        # Main content frame
        content_frame = ctk.CTkFrame(frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=10)
        
        # Title and info frame
        info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)
        
        # Create text container for title and info
        UIHelper.create_text_container(
            info_frame,
            title=download["title"],
            description=f"Format: {download['format']} • Quality: {download['quality']} • Size: {self.format_size(download['size'])}",
            title_font=("Segoe UI", 14),
            desc_font=("Segoe UI", 12),
            title_color="#ffffff",
            desc_color="#888888"
        )
        
        # Add date
        date_label = ctk.CTkLabel(
            info_frame,
            text=datetime.fromtimestamp(download["timestamp"]).strftime("%Y-%m-%d %H:%M"),
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        date_label.pack(side="right")
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        buttons_frame.pack(side="right", padx=(15, 0))
        
        # Open button
        open_button = UIHelper.create_button(
            buttons_frame,
            text="Open",
            command=lambda: self.open_file(download["path"]),
            width=70,
            height=30,
            fg_color=ACCENT_COLOR,
            hover_color=HOVER_COLOR
        )
        open_button.pack(side="left", padx=5)
        
        # Delete button
        delete_button = UIHelper.create_button(
            buttons_frame,
            text="Delete",
            command=lambda: self.delete_download(download, frame),
            width=70,
            height=30,
            fg_color="#d32f2f",
            hover_color="#b71c1c"
        )
        delete_button.pack(side="left", padx=5)

    def format_size(self, size_bytes):
        """Format size in bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    def load_downloads(self):
        """Load downloads from the downloads file"""
        downloads_file = os.path.join(os.path.dirname(__file__), "downloads.json")
        try:
            with open(downloads_file, "r") as f:
                return json.load(f)
        except:
            return {
                "downloads": []
            }

    def add_downloads_sections(self):
        """Add downloads content sections"""
        self.update_search_results(None)

    def open_downloads_folder(self):
        """Open the downloads folder"""
        downloads_dir = os.path.expanduser("~/Downloads")
        os.startfile(downloads_dir)

    def open_file(self, file_path):
        """Open a file with the default application"""
        try:
            os.startfile(file_path)
        except Exception as e:
            print(f"Error opening file: {e}")

    def delete_download(self, download, frame):
        """Delete a download and update the UI"""
        try:
            # Delete the actual file
            if os.path.exists(download["path"]):
                os.remove(download["path"])
            
            # Remove from downloads.json
            downloads_data = self.load_downloads()
            downloads_data["downloads"] = [d for d in downloads_data["downloads"] if d["path"] != download["path"]]
            
            downloads_file = os.path.join(os.path.dirname(__file__), "downloads.json")
            with open(downloads_file, "w") as f:
                json.dump(downloads_data, f, indent=4)
            
            # Remove from UI
            frame.destroy()
            
            # If no downloads left, show empty state
            if not downloads_data["downloads"]:
                self.add_downloads_sections()
                
        except Exception as e:
            print(f"Error deleting download: {e}")

    def handle_back_click(self):
        """Handle back button click"""
        if self.on_back_click:
            # Disable buttons during animation
            self.back_button.configure(state="disabled")
            # Call the callback
            self.on_back_click()

    def clear_search(self):
        """Clear the search entry and reset results"""
        self.search_entry.delete(0, "end")
        self.clear_button.pack_forget()  # Hide clear button
        self.update_search_results(None)
    
    def on_search_change(self, event):
        """Handle search entry changes"""
        # Show/hide clear button based on search content
        if self.search_entry.get():
            self.clear_button.pack(side="left", padx=(8, 0))
        else:
            self.clear_button.pack_forget()
        
        # Update search results
        self.update_search_results(event)

    def update_search_results(self, event):
        """Update the downloads list based on search query"""
        # Clear current content
        for widget in self.content.winfo_children():
            widget.destroy()
            
        # Get search query
        query = self.search_entry.get().lower().strip()
        
        # Load all downloads
        downloads_data = self.load_downloads()
        
        if not downloads_data["downloads"]:
            self.add_section_title("Recent Downloads")
            self.show_empty_state()
            return
            
        # Filter downloads based on search query
        filtered_downloads = []
        for download in downloads_data["downloads"]:
            if query:
                # Search in title, format, and quality
                if (query in download["title"].lower() or
                    query in download["format"].lower() or
                    query in download["quality"].lower()):
                    filtered_downloads.append(download)
            else:
                filtered_downloads.append(download)
        
        # Show results
        if filtered_downloads:
            self.add_section_title("Recent Downloads")
            for download in reversed(filtered_downloads):  # Show newest first
                self.add_download_item(download)
        else:
            self.add_section_title("Search Results")
            self.show_empty_state("No matching downloads found")
    
    def show_empty_state(self, message="No downloads yet"):
        """Show empty state message"""
        empty_frame = ctk.CTkFrame(self.content, fg_color="#232323", corner_radius=8)
        empty_frame.pack(fill="x", pady=5)
        
        empty_label = ctk.CTkLabel(
            empty_frame,
            text=message,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color="#888888"
        )
        empty_label.pack(padx=15, pady=30)

    @staticmethod
    def open(parent_frame, app, on_back_click):
        """Open the downloads page"""
        for widget in parent_frame.winfo_children():
            widget.destroy()
        downloads_frame = DownloadsPage(parent_frame, app, on_back_click=on_back_click)
        downloads_frame.pack(fill="both", expand=True)
        return downloads_frame
