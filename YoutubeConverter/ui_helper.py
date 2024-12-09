import customtkinter as ctk

class UIHelper:
    # Constants for styling
    MENU_WIDTH = 200
    MENU_ITEM_HEIGHT = 45
    MENU_ITEM_FONT_SIZE = 14
    MENU_ICON_SIZE = 20
    MENU_ICON_PADDING = 15
    MENU_TEXT_PADDING = 10
    
    # Updated color scheme
    BG_COLOR = "transparent"
    HOVER_COLOR = "#252525"  # Subtle dark gray for hover
    ACTIVE_COLOR = "#303030"  # Slightly lighter for active state
    TEXT_COLOR = "#E0E0E0"  # Light gray for better readability
    TEXT_HOVER_COLOR = "#FFFFFF"  # Pure white for hover
    DIVIDER_COLOR = "#2A2A2A"  # Subtle divider color
    
    @staticmethod
    def create_title(parent, text, size=16, weight="bold"):
        """Create a title frame with consistent styling"""
        title_frame = ctk.CTkFrame(
            parent,
            fg_color="transparent",
            corner_radius=0
        )
        title_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text=text,
            font=ctk.CTkFont(size=size, weight=weight),
            anchor="w",
            text_color=UIHelper.TEXT_COLOR
        )
        title_label.grid(row=0, column=0, sticky="w", padx=20, pady=10)
        
        # Add subtle divider
        divider = ctk.CTkFrame(
            title_frame,
            height=1,
            fg_color=UIHelper.DIVIDER_COLOR
        )
        divider.grid(row=1, column=0, sticky="ew", padx=10)
        
        return title_frame

    @staticmethod
    def create_menu_item(parent, icon, text, command):
        """Create a menu item button with icon and text"""
        menu_item = ctk.CTkButton(
            parent,
            text=f" {icon} {text}",
            anchor="w",
            fg_color="transparent",
            text_color="#808080",
            hover_color="#333333",
            height=35,
            command=command
        )
        return menu_item

    @staticmethod
    def create_section_frame(parent, **kwargs):
        """Create a section frame with consistent styling"""
        frame = ctk.CTkFrame(parent, **kwargs)
        frame.grid_columnconfigure(0, weight=1)
        return frame
