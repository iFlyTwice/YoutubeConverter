"""Theme management functionality."""

import json
import os
from pathlib import Path
import logging
from typing import Optional, Dict, Any

from .colors import ThemeColors, THEMES

logger = logging.getLogger(__name__)

class ThemeManager:
    """Manages theme settings and operations."""

    def __init__(self) -> None:
        """Initialize the theme manager."""
        self.settings_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "settings.json"
        )

    def save_theme(self, colors: ThemeColors) -> bool:
        """
        Save the current theme to settings.
        
        Args:
            colors: Theme colors to save
        
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            # Load current settings
            if os.path.exists(self.settings_path):
                with open(self.settings_path, 'r') as f:
                    settings = json.load(f)
            else:
                settings = {}
            
            # Find theme name by comparing color values
            theme_name = None
            for name, theme in THEMES.items():
                if (theme.bg == colors.bg and 
                    theme.accent == colors.accent and
                    theme.hover == colors.hover and
                    theme.text == colors.text and
                    theme.secondary_bg == colors.secondary_bg and
                    theme.border == colors.border and
                    theme.secondary_text == colors.secondary_text):
                    theme_name = name
                    break
            
            if theme_name is None:
                theme_name = "Dark Mode"  # Default if no match found
            
            # Update theme name in settings
            settings['theme'] = theme_name
            
            # Save updated settings
            with open(self.settings_path, 'w') as f:
                json.dump(settings, f, indent=4)
            
            return True
        except Exception as e:
            logger.error(f"Error saving theme: {e}")
            return False

    def load_theme(self) -> Optional[ThemeColors]:
        """Load the current theme from settings."""
        try:
            # Default to Dark Mode if settings file doesn't exist
            if not os.path.exists(self.settings_path):
                logger.info("Settings file not found, using Dark Mode")
                return THEMES["Dark Mode"]

            # Read theme from settings
            with open(self.settings_path, 'r') as f:
                settings = json.load(f)
                
            # Get theme name, default to Dark Mode if not found
            theme_name = settings.get('theme', 'Dark Mode')
            if not isinstance(theme_name, str):
                logger.warning(f"Invalid theme name type: {type(theme_name)}, using Dark Mode")
                return THEMES["Dark Mode"]
                
            # Get theme colors, default to Dark Mode if not found
            theme = THEMES.get(theme_name)
            if theme is None:
                logger.warning(f"Theme '{theme_name}' not found, using Dark Mode")
                return THEMES["Dark Mode"]
                
            return theme
                
        except Exception as e:
            logger.error(f"Error loading theme: {e}")
            return THEMES["Dark Mode"]

    def reset_to_default(self) -> Optional[ThemeColors]:
        """Reset to the default Dark Mode theme."""
        try:
            default_theme = THEMES["Dark Mode"]
            self.save_theme(default_theme)
            return default_theme
        except Exception as e:
            logger.error(f"Error resetting theme: {e}")
            return None

    def _get_theme_name(self, colors: ThemeColors) -> str:
        """Get the name of a theme based on its colors."""
        for name, theme in THEMES.items():
            if theme.__dict__ == colors.__dict__:
                return name
        return "Dark Mode"  # Default to Dark Mode if no match found
