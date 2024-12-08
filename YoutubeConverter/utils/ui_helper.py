import customtkinter as ctk
from typing import Optional, Union, Tuple, Any
from PIL import Image


class UIHelper:
    """Helper class for common UI operations and styling"""
    
    # Constants
    MENU_WIDTH = 300  # Width of the sidebar menu in pixels
    
    # Colors
    ACCENT_COLOR = "#3d3d3d"
    HOVER_COLOR = "#4d4d4d"
    TEXT_COLOR = "#ffffff"
    BG_COLOR = "#2d2d2d"

    @staticmethod
    def create_section_frame(
        master: Any,
        height: int = 70,
        fg_color: str = "#232323",
        corner_radius: int = 8
    ) -> ctk.CTkFrame:
        """Create a section frame with standard styling"""
        frame = ctk.CTkFrame(
            master,
            fg_color=fg_color,
            height=height,
            corner_radius=corner_radius
        )
        frame.pack(fill="x", pady=5)
        frame.pack_propagate(False)
        return frame

    @staticmethod
    def create_text_container(
        master: Any,
        title: str,
        description: str,
        title_font: Optional[tuple] = None,
        desc_font: Optional[tuple] = None,
        title_color: str = "#ffffff",
        desc_color: str = "#888888",
        text_align: str = "left"
    ) -> ctk.CTkFrame:
        """Create a text container with title and description"""
        if title_font is None:
            title_font = ("Segoe UI", 13)
        if desc_font is None:
            desc_font = ("Segoe UI", 11)

        text_frame = ctk.CTkFrame(master, fg_color="transparent")
        text_frame.pack(fill="both", expand=True)
        
        title_label = ctk.CTkLabel(
            text_frame,
            text=title,
            font=ctk.CTkFont(family=title_font[0], size=title_font[1]),
            text_color=title_color
        )
        title_label.pack(anchor="center" if text_align == "center" else "w")
        
        if description:
            desc_label = ctk.CTkLabel(
                text_frame,
                text=description,
                font=ctk.CTkFont(family=desc_font[0], size=desc_font[1]),
                text_color=desc_color
            )
            desc_label.pack(anchor="center" if text_align == "center" else "w")
        
        return text_frame

    @staticmethod
    def create_button(
        master: Any,
        text: str,
        command: callable,
        width: int = 70,
        height: int = 32,
        font: Optional[tuple] = None,
        fg_color: str = "#343638",
        hover_color: str = "#2B2B2B",
        text_color: str = "#ffffff",
        corner_radius: int = 8
    ) -> ctk.CTkButton:
        """Create a button with standard styling"""
        if font is None:
            font = ("Segoe UI", 12)
            
        button = ctk.CTkButton(
            master,
            text=text,
            command=command,
            width=width,
            height=height,
            font=ctk.CTkFont(family=font[0], size=font[1]),
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=text_color,
            corner_radius=corner_radius
        )
        return button

    @staticmethod
    def create_entry(
        master: Any,
        width: int = 200,
        height: int = 32,
        font: Optional[tuple] = None,
        placeholder_text: str = "",
        fg_color: str = "#343638",
        border_color: str = "#404040",
        text_color: str = "#ffffff",
        corner_radius: int = 8
    ) -> ctk.CTkEntry:
        """Create an entry field with standard styling"""
        if font is None:
            font = ("Segoe UI", 12)
            
        entry = ctk.CTkEntry(
            master,
            width=width,
            height=height,
            font=ctk.CTkFont(family=font[0], size=font[1]),
            placeholder_text=placeholder_text,
            fg_color=fg_color,
            border_color=border_color,
            text_color=text_color,
            corner_radius=corner_radius
        )
        return entry

    @staticmethod
    def create_label(parent, text, font=("Segoe UI", 12), wraplength=None, justify="left", text_color="#ffffff"):
        """Create a standardized label with proper wraplength handling"""
        kwargs = {
            "master": parent,  # CTkLabel requires 'master' instead of 'parent'
            "text": text,
            "font": font,
            "justify": justify,
            "text_color": text_color
        }
        
        # Only add wraplength if it's a positive number
        if wraplength and wraplength > 0:
            kwargs["wraplength"] = wraplength
            
        return ctk.CTkLabel(**kwargs)

    @staticmethod
    def create_dropdown(parent, values, variable, width=120, height=28):
        """Create a standardized dropdown menu"""
        return ctk.CTkOptionMenu(
            master=parent,  # Use master instead of parent
            values=values,
            variable=variable,
            width=width,
            height=height,
            font=("Segoe UI", 12),
            fg_color="#2d2d2d",
            button_color="#363636",
            button_hover_color="#404040",
            dropdown_fg_color="#2d2d2d",
            dropdown_hover_color="#404040",
            corner_radius=6
        )

    @staticmethod
    def ease_out_quad(t: float) -> float:
        """Quadratic ease-out function for smooth animations
        Args:
            t: Progress from 0.0 to 1.0
        Returns:
            Eased value from 0.0 to 1.0
        """
        return t * (2 - t)

    @staticmethod
    def resize_image(image: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        """
        Resize an image to target size while maintaining aspect ratio
        
        Args:
            image: PIL Image object to resize
            target_size: Tuple of (width, height) for target size
            
        Returns:
            Resized PIL Image object
        """
        original_width, original_height = image.size
        target_width, target_height = target_size
        
        # Calculate aspect ratios
        original_aspect = original_width / original_height
        target_aspect = target_width / target_height
        
        if original_aspect > target_aspect:
            # Image is wider than target - scale by width
            new_width = target_width
            new_height = int(target_width / original_aspect)
        else:
            # Image is taller than target - scale by height
            new_height = target_height
            new_width = int(target_height * original_aspect)
            
        # Resize the image
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create a new blank image with the target size
        final_image = Image.new("RGB", target_size, (0, 0, 0))
        
        # Calculate position to paste resized image (center it)
        paste_x = (target_width - new_width) // 2
        paste_y = (target_height - new_height) // 2
        
        # Paste the resized image onto the blank canvas
        final_image.paste(resized_image, (paste_x, paste_y))
        
        return final_image
