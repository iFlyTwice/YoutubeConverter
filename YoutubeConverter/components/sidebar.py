import customtkinter as ctk
import sys
import os
from PIL import Image

# Add the parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from YoutubeConverter.utils.ui_helper import UIHelper

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, width=300, fg_color="#1a1a1a", **kwargs)
        
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create menu label
        self.menu_label = ctk.CTkLabel(
            self,
            text="MENU",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#808080"
        )
        self.menu_label.grid(row=0, column=0, padx=25, pady=(20, 15), sticky="w")
        
        # Create regular frame for menu items (no scrollbar)
        self.menu_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.menu_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 10))
        
        # Configure menu frame grid
        self.menu_frame.grid_columnconfigure(0, weight=1)
        
        # List to store menu items
        self.menu_items = []
        
    def add_menu_item(self, text: str, icon: str, command=None):
        """Add a menu item to the sidebar"""
        button = ctk.CTkButton(
            self.menu_frame,
            text=f"{icon}  {text}",
            compound="left",
            anchor="w",
            font=ctk.CTkFont(size=15),
            height=45,
            fg_color="transparent",
            text_color="#ffffff",
            hover_color="#2a2a2a",
            command=command
        )
        button.grid(row=len(self.menu_items), column=0, padx=12, pady=6, sticky="ew")
        self.menu_items.append(button)
        
    def on_home_click(self):
        """Handle home button click"""
        # This will be handled by the main app
        if hasattr(self.master, 'transition_to_main'):
            self.master.transition_to_main()
