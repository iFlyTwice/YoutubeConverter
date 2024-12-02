import customtkinter as ctk

class CustomDropdown(ctk.CTkOptionMenu):
    def __init__(self, master, values=None, command=None, width=140, **kwargs):
        """
        A custom dropdown widget that extends CTkOptionMenu with additional styling and functionality.
        
        Args:
            master: The parent widget
            values: List of values to display in the dropdown
            command: Callback function when an option is selected
            width: Width of the dropdown
            **kwargs: Additional keyword arguments passed to CTkOptionMenu
        """
        if values is None:
            values = []
            
        super().__init__(
            master=master,
            values=values,
            command=command,
            width=width,
            fg_color="#2B2B2B",  # Dark background
            button_color="#3B3B3B",  # Slightly lighter button
            button_hover_color="#4B4B4B",  # Hover effect
            dropdown_fg_color="#2B2B2B",  # Dropdown background
            dropdown_hover_color="#4B4B4B",  # Hover color for dropdown items
            dropdown_text_color="white",  # Text color
            **kwargs
        )
        
    def configure(self, **kwargs):
        """Configure the dropdown with new options."""
        super().configure(**kwargs)
        
    def set(self, value):
        """Set the current value of the dropdown."""
        super().set(value)
