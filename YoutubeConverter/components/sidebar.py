import customtkinter as ctk
import threading
import time
from utils.ui_helper import UIHelper

class SmoothSidebar(ctk.CTkFrame):
    def __init__(self, master, width=250, **kwargs):
        # Set width in the constructor and add corner radius
        kwargs["width"] = width
        kwargs["corner_radius"] = 12
        kwargs["border_width"] = 2
        kwargs["border_color"] = "#404040"
        super().__init__(master, **kwargs)
        
        self.width = width
        self.visible = False
        self.animating = False
        
        # Configure the sidebar with a darker theme
        self.configure(fg_color="#1a1a1a")
        
        # Create a container for content
        self.content_frame = UIHelper.create_section_frame(
            self,
            height=0,  # Let it expand
            fg_color="transparent",
            corner_radius=0
        )
        self.content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Menu title with modern styling
        title_frame = UIHelper.create_section_frame(
            self.content_frame,
            height=50,
            fg_color="transparent",
            corner_radius=0
        )
        title_frame.pack(fill="x", pady=(10, 5))
        
        # Create title text container with improved font
        UIHelper.create_text_container(
            title_frame,
            title="MENU",
            description="",
            title_font=("Arial", 24, "bold"),
            title_color="#FFFFFF"
        ).pack(side="left", padx=(5, 0))

        # Add white separator line with increased visibility
        separator = UIHelper.create_section_frame(
            self.content_frame,
            height=1,  # Reduced to 1px
            fg_color="#FFFFFF",
            corner_radius=0
        )
        separator.pack(fill="x", pady=(5, 15))
        
        # Modern separator with gradient effect
        separator_frame = UIHelper.create_section_frame(
            self.content_frame,
            height=2,
            fg_color="transparent",
            corner_radius=0
        )
        separator_frame.pack(fill="x", pady=(0, 25))
        
        # Create two separators for gradient effect
        sep1 = UIHelper.create_section_frame(
            separator_frame,
            height=1,
            fg_color="#404040",
            corner_radius=0
        )
        sep1.pack(fill="x")
        
        sep2 = UIHelper.create_section_frame(
            separator_frame,
            height=1,
            fg_color="#0d0d0d",
            corner_radius=0
        )
        sep2.pack(fill="x")
        
        # Initially place the sidebar off-screen with a small offset
        self.place(relx=1.0, rely=0, relheight=1, x=2)
        
        # Bind click events
        self.master.bind("<Button-1>", self.check_click_outside)
        self.bind("<Button-1>", self.on_sidebar_click)

    def add_menu_item(self, icon, text, command=None):
        """Add a styled menu item to the sidebar"""
        # Create frame for better layout control
        frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        frame.pack(fill="x", pady=4)

        # Create icon label
        icon_label = ctk.CTkLabel(
            frame,
            text=icon,
            font=ctk.CTkFont(family="Segoe UI", size=16),
            text_color="#ffffff",
            width=25
        )
        icon_label.pack(side="left", padx=(10, 5))

        # Create button
        button = ctk.CTkButton(
            frame,
            text=text,
            command=command,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            fg_color="transparent",
            text_color="#e0e0e0",
            hover_color="#2d2d2d",
            anchor="w",
            height=40,
            corner_radius=8
        )
        button.pack(fill="x", padx=(0, 10))
        return button

    def on_sidebar_click(self, event):
        return "break"
        
    def check_click_outside(self, event):
        if not self.visible:
            return
            
        clicked_widget = event.widget
        parent = clicked_widget
        while parent is not None:
            if parent == self:
                return
            parent = parent.master
            
        self.toggle()

    def toggle(self):
        if self.animating:
            return
            
        self.animating = True
        
        if self.visible:
            def hide_animation():
                try:
                    steps = 12  # Reduced steps for faster animation
                    start_x = 1.0 - self.width/self.master.winfo_width()
                    end_x = 1.0
                    
                    for i in range(steps + 1):
                        if not self.animating:
                            break
                        t = i / steps
                        # Use ease-out function for smoother animation
                        t = 1 - (1 - t) * (1 - t)
                        current_x = start_x + (end_x - start_x) * t
                        self.place(relx=current_x, rely=0, relheight=1, x=2)
                        self.update()
                        time.sleep(0.001)  # Reduced delay for faster animation
                        
                    self.visible = False
                finally:
                    self.animating = False
                    
            threading.Thread(target=hide_animation, daemon=True).start()
        else:
            def show_animation():
                try:
                    steps = 12  # Reduced steps for faster animation
                    start_x = 1.0
                    end_x = 1.0 - self.width/self.master.winfo_width()
                    
                    for i in range(steps + 1):
                        if not self.animating:
                            break
                        t = i / steps
                        # Use ease-out function for smoother animation
                        t = 1 - (1 - t) * (1 - t)
                        current_x = start_x + (end_x - start_x) * t
                        self.place(relx=current_x, rely=0, relheight=1, x=2)
                        self.update()
                        time.sleep(0.001)  # Reduced delay for faster animation
                        
                    self.visible = True
                finally:
                    self.animating = False
                    
            threading.Thread(target=show_animation, daemon=True).start()
