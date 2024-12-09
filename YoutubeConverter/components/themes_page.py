"""
Theme selection and management page for the YouTube Converter application.
Allows users to view and apply different theme options.
"""

import customtkinter as ctk
from typing import TYPE_CHECKING, Optional, Any
import logging
import os
import sys

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # YoutubeConverter directory
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Configure logging
logger = logging.getLogger(__name__)

from config.themes import (
    ThemeManager, ThemeColors, THEMES,
    update_widget_tree
)
from utils.ui_helper import UIHelper

if TYPE_CHECKING:
    from modern_youtube_converter import YoutubeConverterApp

logger = logging.getLogger(__name__)

class ThemesPage(ctk.CTkFrame):
    """
    A page for managing application themes.
    Displays available themes and allows users to preview and apply them.
    """

    def __init__(self, master: Any, app: Optional['YoutubeConverterApp'] = None) -> None:
        """Initialize the themes page"""
        super().__init__(master)
        self.app = app
        self.theme_manager = ThemeManager()
        self.theme_cards = {}  # Store theme cards for updating
        self.separators = []  # Store separators for updating
        
        try:
            self._setup_ui()
            # Update all theme cards with current theme immediately
            current_theme = self.theme_manager.load_theme()
            current_theme = current_theme if isinstance(current_theme, ThemeColors) else THEMES["Dark Mode"]
            self._update_theme_cards(current_theme)
        except Exception as e:
            logger.error(f"Error initializing ThemesPage: {e}")
            raise

    def _setup_ui(self) -> None:
        """Set up the UI components"""
        try:
            # Configure the frame with current theme
            if self.app and hasattr(self.app, 'theme') and isinstance(self.app.theme, ThemeColors):
                current_theme = self.app.theme
            else:
                loaded_theme = self.theme_manager.load_theme()
                current_theme = loaded_theme if isinstance(loaded_theme, ThemeColors) else THEMES["Dark Mode"]
                
            self.configure(fg_color=current_theme.bg, corner_radius=0)
            
            # Configure grid
            self.grid_rowconfigure(0, weight=1)
            self.grid_columnconfigure(0, weight=1)
            
            # Create main container
            self.main_container = ctk.CTkFrame(self, fg_color="transparent")
            self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Create header
            header_container = ctk.CTkFrame(
                self.main_container,
                height=70,
                fg_color="#1a1a1a",
                corner_radius=12,
                border_width=2,
                border_color="#404040"
            )
            header_container.pack(fill="x", padx=20, pady=(20, 15))
            header_container.pack_propagate(False)

            # Back button
            self.back_button = ctk.CTkButton(
                header_container,
                text="←",
                command=self.handle_back_click,
                width=40,
                height=40,
                font=ctk.CTkFont(size=20),
                fg_color="transparent",
                hover_color="#3d3d3d",
                corner_radius=8
            )
            self.back_button.pack(side="left", padx=15)

            # Title label
            title_label = ctk.CTkLabel(
                header_container,
                text="Themes",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#FFFFFF"
            )
            title_label.pack(side="left", padx=15)
            
            # Separator after header
            separator = ctk.CTkFrame(
                self.main_container,
                height=2,
                fg_color="#404040"
            )
            separator.pack(fill="x", padx=20, pady=(5, 15))
            
            # Built-in Themes section
            themes_section = ctk.CTkFrame(
                self.main_container,
                fg_color="#1a1a1a",
                corner_radius=12,
                border_width=2,
                border_color="#404040"
            )
            themes_section.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
            # Built-in Themes label
            builtin_label = ctk.CTkLabel(
                themes_section,
                text="Built-in Themes",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="#FFFFFF",
                anchor="w"
            )
            builtin_label.pack(fill="x", padx=15, pady=15)
            
            # Separator under label
            label_separator = ctk.CTkFrame(
                themes_section,
                height=1,
                fg_color="#404040"
            )
            label_separator.pack(fill="x", padx=15, pady=(0, 15))

            # Create scrollable container for themes
            self.themes_container = ctk.CTkScrollableFrame(
                themes_section,
                fg_color="transparent",
                corner_radius=0
            )
            self.themes_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

            # Create theme cards
            self._create_theme_cards()
            
        except Exception as e:
            logger.error(f"Error in _setup_ui: {e}")
            raise

    def _create_theme_cards(self) -> None:
        """Create and populate theme cards"""
        try:
            # Clear existing cards
            for widget in self.themes_container.winfo_children():
                widget.destroy()
            self.theme_cards.clear()
            
            # Create cards for each theme
            for theme_name, theme in THEMES.items():
                card = self._create_theme_card(theme_name, theme)
                card.pack(fill="x", pady=(0, 10))
                self.theme_cards[theme_name] = card
                
            # Force update
            self.update_idletasks()
            
        except Exception as e:
            logger.error(f"Error creating theme cards: {e}")
            raise

    def _create_theme_card(self, theme_name: str, theme: ThemeColors) -> ctk.CTkFrame:
        """Create a theme card with preview box and apply button"""
        try:
            # Create card frame
            card = ctk.CTkFrame(
                self.themes_container,
                fg_color="#1a1a1a",
                corner_radius=12,
                border_width=2,
                border_color="#404040"
            )
            
            # Create content layout
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(fill="both", expand=True, padx=15, pady=15)
            
            # Left side: Theme info
            info = ctk.CTkFrame(content, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True)
            
            # Theme name
            name = ctk.CTkLabel(
                info,
                text=theme_name,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#FFFFFF",
                anchor="w"
            )
            name.pack(fill="x", pady=(0, 5))
            
            # Color info
            colors = ctk.CTkLabel(
                info,
                text=f"Background: {theme.bg}, Accent: {theme.accent}",
                font=ctk.CTkFont(size=12),
                text_color="#808080",
                anchor="w"
            )
            colors.pack(fill="x")
            
            # Right side: Color previews
            preview = ctk.CTkFrame(content, fg_color="transparent", width=100)
            preview.pack(side="right", padx=(10, 0))
            preview.pack_propagate(False)
            
            # Background color preview
            bg_preview = ctk.CTkFrame(
                preview,
                width=45,
                height=45,
                fg_color=theme.bg,
                corner_radius=6,
                border_width=1,
                border_color="#404040"
            )
            bg_preview.pack(side="left", padx=(0, 5))
            bg_preview.pack_propagate(False)
            
            # Accent color preview
            accent_preview = ctk.CTkFrame(
                preview,
                width=45,
                height=45,
                fg_color=theme.accent,
                corner_radius=6,
                border_width=1,
                border_color="#404040"
            )
            accent_preview.pack(side="left")
            accent_preview.pack_propagate(False)
            
            # Store preview references
            card.bg_preview = bg_preview
            card.accent_preview = accent_preview
            
            # Apply button
            apply_btn = ctk.CTkButton(
                content,
                text="Apply",
                width=80,
                height=32,
                command=lambda t=theme_name: self.apply_theme(t),
                fg_color=theme.accent,
                hover_color=theme.hover,
                corner_radius=8
            )
            apply_btn.pack(side="right", padx=(10, 0))
            
            return card
            
        except Exception as e:
            logger.error(f"Error creating theme card for {theme_name}: {e}")
            raise

    def _update_theme_cards(self, current_theme: ThemeColors) -> None:
        """Update theme cards to maintain their preview colors"""
        for theme_name, card in self.theme_cards.items():
            theme = THEMES[theme_name]
            
            # Update preview colors
            if hasattr(card, 'bg_preview'):
                card.bg_preview.configure(fg_color=theme.bg)
            if hasattr(card, 'accent_preview'):
                card.accent_preview.configure(fg_color=theme.accent)
            
            # Update card background based on current theme
            card_bg = "#1a1a1a" if current_theme.bg.startswith("#") else "#f0f0f0"
            card.configure(fg_color=card_bg)
            
            # Update button colors
            for widget in card.winfo_children():
                if isinstance(widget, ctk.CTkButton):
                    widget.configure(
                        fg_color=theme.accent,
                        hover_color=theme.hover
                    )
            
        # Update scrollbar colors based on theme
        if current_theme.bg.startswith("#f"):  # Light theme
            scrollbar_color = "#d0d0d0"  # Light gray for scrollbar
            # Update back button for light theme
            self.back_button.configure(
                text_color="#000000",  # Black text
                hover_color="#d0d0d0"  # Light gray hover
            )
        else:  # Dark theme
            scrollbar_color = "#3d3d3d"  # Dark gray for scrollbar
            # Update back button for dark theme
            self.back_button.configure(
                text_color="#ffffff",  # White text
                hover_color="#3d3d3d"  # Dark gray hover
            )
            
        # Update content area with proper scrollbar colors
        self.themes_container.configure(
            fg_color="transparent",
            scrollbar_button_color=scrollbar_color,
            scrollbar_button_hover_color=scrollbar_color
        )

    def apply_theme(self, theme_name: str) -> None:
        """
        Apply the selected theme to the application.
        
        Args:
            theme_name: Name of the theme to apply
        """
        try:
            # Get the root window (app instance)
            root = self.master.master
        
            # Get the theme colors
            theme = THEMES[theme_name]
        
            # Update window colors
            root.configure(fg_color=theme.bg)
        
            # Update all widgets in the application
            update_widget_tree(root, theme)
        
            # Update theme cards container backgrounds
            self._update_theme_cards(theme)
        
            # If app instance is available, store theme
            if self.app:
                self.app.theme = theme
                # Save theme to settings
                if not self.theme_manager.save_theme(theme):
                    logger.error("Failed to save theme settings")
                    return
            
            # Update current page colors
            self.configure(fg_color=theme.bg)
            
            # Force a redraw of the entire window
            root.update_idletasks()
        
        except Exception as e:
            logger.error(f"Error applying theme: {e}")

    def handle_back_click(self) -> None:
        """Handle back button click"""
        try:
            if self.app:
                from components.main_page import MainPage  # Import at function level to avoid circular imports
                self.app.transition_to_page(MainPage)
        except Exception as e:
            logger.error(f"Error handling back click: {e}")
