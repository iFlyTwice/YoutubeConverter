"""
Utility functions for applying themes to widgets.
"""

import customtkinter as ctk
from typing import Any
from .colors import ThemeColors

def configure_button(button: ctk.CTkButton, colors: ThemeColors) -> None:
    """
    Configure button with theme colors.
    
    Args:
        button: Button widget to configure
        colors: Theme colors to apply
    """
    if button.cget('fg_color') not in ('transparent', None):
        button.configure(
            fg_color=colors.accent,
            hover_color=colors.hover,
            text_color=colors.text,
            border_color=colors.border
        )

def configure_frame(frame: ctk.CTkFrame, colors: ThemeColors) -> None:
    """
    Configure frame with theme colors.
    
    Args:
        frame: Frame widget to configure
        colors: Theme colors to apply
    """
    if frame.cget('fg_color') not in ('transparent', None):
        is_card = any(name in str(frame).lower() for name in ['card', 'preview', 'header'])
        frame.configure(
            fg_color=colors.secondary_bg if is_card else colors.bg,
            border_color=colors.border
        )

def configure_label(label: ctk.CTkLabel, colors: ThemeColors) -> None:
    """
    Configure label with theme colors.
    
    Args:
        label: Label widget to configure
        colors: Theme colors to apply
    """
    is_secondary = any(name in str(label).lower() 
                      for name in ['desc', 'description', 'subtitle', 'secondary'])
    label.configure(
        text_color=colors.secondary_text if is_secondary else colors.text
    )

def configure_entry(entry: ctk.CTkEntry, colors: ThemeColors) -> None:
    """
    Configure entry with theme colors.
    
    Args:
        entry: Entry widget to configure
        colors: Theme colors to apply
    """
    entry.configure(
        fg_color=colors.secondary_bg,
        border_color=colors.border,
        text_color=colors.text,
        placeholder_text_color=colors.secondary_text
    )

def configure_progress_bar(progress_bar: ctk.CTkProgressBar, colors: ThemeColors) -> None:
    """
    Configure progress bar with theme colors.
    
    Args:
        progress_bar: Progress bar widget to configure
        colors: Theme colors to apply
    """
    progress_bar.configure(
        fg_color=colors.accent,
        progress_color=colors.hover,
        border_color=colors.border
    )

def configure_scrollable_frame(frame: ctk.CTkScrollableFrame, colors: ThemeColors) -> None:
    """
    Configure scrollable frame with theme colors.
    
    Args:
        frame: Scrollable frame widget to configure
        colors: Theme colors to apply
    """
    frame.configure(
        fg_color=colors.bg,
        border_color=colors.border
    )

def configure_textbox(textbox: ctk.CTkTextbox, colors: ThemeColors) -> None:
    """
    Configure textbox with theme colors.
    
    Args:
        textbox: Textbox widget to configure
        colors: Theme colors to apply
    """
    textbox.configure(
        fg_color=colors.secondary_bg,
        border_color=colors.border,
        text_color=colors.text
    )

def configure_segmented_button(button: ctk.CTkSegmentedButton, colors: ThemeColors) -> None:
    """
    Configure segmented button with theme colors.
    
    Args:
        button: Segmented button widget to configure
        colors: Theme colors to apply
    """
    button.configure(
        fg_color=colors.accent,
        selected_color=colors.hover,
        selected_hover_color=colors.hover,
        unselected_color=colors.secondary_bg,
        unselected_hover_color=colors.hover,
        text_color=colors.text,
        border_color=colors.border
    )

def update_widget_tree(root: Any, colors: ThemeColors) -> None:
    """
    Recursively update all widgets in a widget tree with theme colors.
    
    Args:
        root: Root widget to start from
        colors: Theme colors to apply
    """
    widget_configurators = {
        ctk.CTkButton: configure_button,
        ctk.CTkFrame: configure_frame,
        ctk.CTkLabel: configure_label,
        ctk.CTkEntry: configure_entry,
        ctk.CTkProgressBar: configure_progress_bar,
        ctk.CTkScrollableFrame: configure_scrollable_frame,
        ctk.CTkTextbox: configure_textbox,
        ctk.CTkSegmentedButton: configure_segmented_button
    }
    
    try:
        # Configure the root widget if it has a matching configurator
        widget_type = type(root)
        if widget_type in widget_configurators:
            widget_configurators[widget_type](root, colors)
        
        # Recursively update all child widgets
        for child in root.winfo_children():
            update_widget_tree(child, colors)
            
    except Exception as e:
        print(f"Error updating widget {root}: {e}")
