"""
Theme color definitions and color management utilities.
"""

from dataclasses import dataclass
from typing import Dict

@dataclass
class ThemeColors:
    """
    Represents a complete theme color scheme.
    Each color should be a valid hex color code (e.g., '#ffffff').
    """
    bg: str  # Main background color
    accent: str  # Primary accent color
    hover: str  # Hover state color
    text: str  # Primary text color
    secondary_bg: str  # Secondary background color (for cards, etc.)
    border: str  # Border color
    secondary_text: str  # Secondary text color (for descriptions, etc.)

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'ThemeColors':
        """Create a ThemeColors instance from a dictionary"""
        return cls(
            bg=data['bg'],
            accent=data['accent'],
            hover=data['hover'],
            text=data['text'],
            secondary_bg=data['secondary_bg'],
            border=data['border'],
            secondary_text=data['secondary_text']
        )

    def to_dict(self) -> Dict[str, str]:
        """Convert ThemeColors to a dictionary"""
        return {
            'bg': self.bg,
            'accent': self.accent,
            'hover': self.hover,
            'text': self.text,
            'secondary_bg': self.secondary_bg,
            'border': self.border,
            'secondary_text': self.secondary_text
        }

# Built-in theme definitions
THEMES = {
    "Dark Mode": ThemeColors(
        bg="#1a1a1a",
        accent="#3d3d3d",
        hover="#4d4d4d",
        text="#ffffff",
        secondary_bg="#232323",
        border="#2d2d2d",
        secondary_text="#888888"
    ),
    "Light Mode": ThemeColors(
        bg="#f8f9fa",  # Softer white background
        accent="#e9ecef",  # Soft gray accent
        hover="#dee2e6",  # Slightly darker hover
        text="#212529",  # Dark gray text
        secondary_bg="#ffffff",  # Pure white for cards
        border="#ced4da",  # Medium gray border
        secondary_text="#6c757d"  # Medium gray text
    ),
    "Night Blue": ThemeColors(
        bg="#1a1f3c",
        accent="#2d3657",
        hover="#3d4667",
        text="#ffffff",
        secondary_bg="#242b4a",
        border="#2d3657",
        secondary_text="#a0a8c9"
    ),
    "Forest Green": ThemeColors(
        bg="#1a3c1f",
        accent="#2d572f",
        hover="#3d673f",
        text="#ffffff",
        secondary_bg="#244028",
        border="#2d572f",
        secondary_text="#a0c9a3"
    )
}
