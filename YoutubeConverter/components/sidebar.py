import customtkinter as ctk
import threading
import time

class SmoothSidebar(ctk.CTkFrame):
    def __init__(self, master, width=250, **kwargs):
        # Set width in the constructor and add corner radius
        kwargs["width"] = width
        kwargs["corner_radius"] = 12
        kwargs["border_width"] = 2  # Increased border width
        kwargs["border_color"] = "#404040"  # Lighter border color
        super().__init__(master, **kwargs)
        
        self.width = width
        self.visible = False
        self.animating = False
        
        # Configure the sidebar with a darker theme
        self.configure(fg_color="#1a1a1a")  # Darker background
        
        # Create a scrollable frame for content with padding
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_fg_color="#2B2B2B",
            scrollbar_button_color="#3B3B3B",
            scrollbar_button_hover_color="#4B4B4B"
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Menu title with modern styling
        title_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(10, 20))
        
        self.menu_title = ctk.CTkLabel(
            title_frame,
            text="Menu",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color="#ffffff"
        )
        self.menu_title.pack(side="left")

        # Modern separator with gradient effect
        separator_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent", height=2)
        separator_frame.pack(fill="x", pady=(0, 25))
        
        # Create two separators for gradient effect
        sep1 = ctk.CTkFrame(separator_frame, fg_color="#404040", height=1)  # Matching border color
        sep1.pack(fill="x")
        sep2 = ctk.CTkFrame(separator_frame, fg_color="#0d0d0d", height=1)
        sep2.pack(fill="x")
        
        # Initially place the sidebar off-screen with a small offset to show right border
        self.place(relx=1.0, rely=0, relheight=1, x=2)  # Added x offset
        
        # Bind click events
        self.master.bind("<Button-1>", self.check_click_outside)
        self.bind("<Button-1>", self.on_sidebar_click)

    def add_menu_item(self, icon, text, command=None):
        """Add a styled menu item to the sidebar"""
        button = ctk.CTkButton(
            self.scrollable_frame,
            text=f" {icon}  {text}",  # Extra space for better icon alignment
            command=command,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            fg_color="transparent",
            text_color="#e0e0e0",
            hover_color="#2d2d2d",
            anchor="w",
            height=40,
            corner_radius=8
        )
        button.pack(fill="x", pady=4)
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
