import customtkinter as ctk
import json
import os

DARKER_COLOR = "#1a1a1a"
ACCENT_COLOR = "#333333"
HOVER_COLOR = "#404040"
TEXT_COLOR = "#ffffff"

class ThemesPage(ctk.CTkFrame):
    def __init__(self, master, on_back_click=None, **kwargs):
        super().__init__(master, **kwargs)
        
        # Store callback
        self.on_back_click = on_back_click
        
        # Configure the frame
        self.configure(fg_color="#1a1a1a", corner_radius=12)
        
        # Create header
        self.header = ctk.CTkFrame(self, fg_color="#232323", height=60, corner_radius=12)
        self.header.pack(fill="x", padx=15, pady=(15, 0))
        self.header.pack_propagate(False)
        
        # Add back button with arrow
        self.back_button = ctk.CTkButton(
            self.header,
            text="←",  # Left arrow
            width=40,
            height=40,
            font=ctk.CTkFont(size=20),
            fg_color="transparent",
            hover_color="#3d3d3d",
            corner_radius=8,
            command=self.handle_back_click
        )
        self.back_button.pack(side="left", padx=10)
        
        # Add title to header
        self.title = ctk.CTkLabel(
            self.header,
            text="Themes",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#ffffff"
        )
        self.title.pack(side="left", padx=(5, 20))
        
        # Add close button
        self.close_button = ctk.CTkButton(
            self.header,
            text="×",
            width=40,
            height=40,
            font=ctk.CTkFont(size=20),
            fg_color="transparent",
            hover_color="#3d3d3d",
            corner_radius=8,
            command=self.handle_back_click
        )
        self.close_button.pack(side="right", padx=10)
        
        # Create content area with scrollable frame
        self.content = ctk.CTkScrollableFrame(
            self,
            fg_color="#1a1a1a",
            corner_radius=0
        )
        self.content.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Add themes content
        self.add_themes_sections()
    
    def add_section_title(self, text):
        """Add a section title to the themes page"""
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

    def add_theme_button(self, name, colors):
        """Add a theme button with preview"""
        frame = ctk.CTkFrame(self.content, fg_color="#232323", height=70, corner_radius=8)
        frame.pack(fill="x", pady=5)
        frame.pack_propagate(False)
        
        # Preview container
        preview_frame = ctk.CTkFrame(frame, fg_color=colors["bg"], width=100, corner_radius=4)
        preview_frame.pack(side="left", padx=15, pady=10, fill="y")
        
        # Sample elements in preview
        sample_button = ctk.CTkButton(
            preview_frame,
            text="",
            width=60,
            height=20,
            fg_color=colors["accent"],
            hover_color=colors["hover"]
        )
        sample_button.pack(padx=5, pady=5)
        
        # Theme name and description
        text_frame = ctk.CTkFrame(frame, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True, padx=(0, 15), pady=10)
        
        name_label = ctk.CTkLabel(
            text_frame,
            text=name,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#ffffff"
        )
        name_label.pack(anchor="w")
        
        desc_label = ctk.CTkLabel(
            text_frame,
            text=f"Background: {colors['bg']}, Accent: {colors['accent']}",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#888888"
        )
        desc_label.pack(anchor="w")
        
        # Apply button
        apply_button = ctk.CTkButton(
            frame,
            text="Apply",
            width=80,
            fg_color=ACCENT_COLOR,
            hover_color=HOVER_COLOR,
            command=lambda: self.apply_theme(colors)
        )
        apply_button.pack(side="right", padx=15)

    def add_themes_sections(self):
        """Add themes content sections"""
        # Built-in Themes Section
        self.add_section_title("Built-in Themes")
        
        themes = {
            "Dark Mode": {
                "bg": "#1a1a1a",
                "accent": "#3d3d3d",
                "hover": "#4d4d4d",
                "text": "#ffffff"
            },
            "Light Mode": {
                "bg": "#f0f0f0",
                "accent": "#e0e0e0",
                "hover": "#d0d0d0",
                "text": "#000000"
            },
            "Night Blue": {
                "bg": "#1a1f3c",
                "accent": "#2d3657",
                "hover": "#3d4667",
                "text": "#ffffff"
            },
            "Forest Green": {
                "bg": "#1a3c1f",
                "accent": "#2d572f",
                "hover": "#3d673f",
                "text": "#ffffff"
            }
        }
        
        for name, colors in themes.items():
            self.add_theme_button(name, colors)
        
        # Custom Theme Section
        self.add_section_title("Custom Theme")
        custom_frame = ctk.CTkFrame(self.content, fg_color="#232323", corner_radius=8)
        custom_frame.pack(fill="x", pady=5)
        
        custom_label = ctk.CTkLabel(
            custom_frame,
            text="Create your own theme by customizing colors",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color="#ffffff"
        )
        custom_label.pack(padx=15, pady=(15, 5))
        
        # Color picker buttons (placeholder for now)
        colors_frame = ctk.CTkFrame(custom_frame, fg_color="transparent")
        colors_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        bg_button = ctk.CTkButton(
            colors_frame,
            text="Background Color",
            fg_color=ACCENT_COLOR,
            hover_color=HOVER_COLOR
        )
        bg_button.pack(side="left", padx=5)
        
        accent_button = ctk.CTkButton(
            colors_frame,
            text="Accent Color",
            fg_color=ACCENT_COLOR,
            hover_color=HOVER_COLOR
        )
        accent_button.pack(side="left", padx=5)
        
        text_button = ctk.CTkButton(
            colors_frame,
            text="Text Color",
            fg_color=ACCENT_COLOR,
            hover_color=HOVER_COLOR
        )
        text_button.pack(side="left", padx=5)

    def apply_theme(self, colors):
        """Apply the selected theme"""
        # Save theme to settings
        settings_file = os.path.join(os.path.dirname(__file__), "settings.json")
        try:
            with open(settings_file, "r") as f:
                settings = json.load(f)
        except:
            settings = {}
        
        settings["theme"] = colors
        
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=4)
        
        # Update UI colors
        self.master.master.configure(fg_color=colors["bg"])
        # TODO: Update other UI elements with new colors

    def handle_back_click(self):
        """Handle back button click"""
        if self.on_back_click:
            # Disable buttons during animation
            self.back_button.configure(state="disabled")
            self.close_button.configure(state="disabled")
            # Call the callback
            self.on_back_click()

    @staticmethod
    def open(parent_frame, on_back_click):
        """Open the themes page"""
        for widget in parent_frame.winfo_children():
            widget.destroy()
        themes_frame = ThemesPage(parent_frame, on_back_click=on_back_click)
        themes_frame.pack(fill="both", expand=True)
        return themes_frame
