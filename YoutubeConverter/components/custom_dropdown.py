import customtkinter as ctk
from typing import List, Optional, Callable, Any

class CustomDropdown(ctk.CTkFrame):
    def __init__(
        self,
        master: Any,
        values: List[str],
        command: Optional[Callable[[str], None]] = None,
        width: int = 140,
        height: int = 28,
        corner_radius: int = 6,
        fg_color: str = "#343638",
        button_color: str = "#343638",
        button_hover_color: str = "#2B2B2B",
        dropdown_fg_color: str = "#343638",
        dropdown_hover_color: str = "#2B2B2B",
        text_color: str = "#DCE4EE",
        font: Optional[tuple] = None,
        **kwargs
    ):
        # Remove appearance mode properties from kwargs
        if "bg_color" in kwargs:
            del kwargs["bg_color"]
        if "border_width" in kwargs:
            del kwargs["border_width"]

        super().__init__(
            master,
            width=width,
            height=height,
            fg_color="transparent",
            corner_radius=corner_radius,
            **kwargs
        )

        self.values = values
        self.command = command
        self.current_value = values[0] if values else ""
        self.is_open = False
        self.dropdown_frame = None

        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create main button
        self.main_button = ctk.CTkButton(
            self,
            text=self.current_value + " ▾",
            width=width,
            height=height,
            fg_color=button_color,
            hover_color=button_hover_color,
            text_color=text_color,
            font=font,
            corner_radius=corner_radius,
            command=self.toggle_dropdown
        )
        self.main_button.grid(row=0, column=0, sticky="nsew")

    def toggle_dropdown(self, event=None):
        """Toggle the dropdown visibility"""
        if self.is_open:
            self.close_dropdown()
        else:
            self.open_dropdown()

    def open_dropdown(self):
        """Open the dropdown"""
        if self.is_open:
            return

        self.is_open = True
        
        # Create dropdown window using CTkToplevel
        self.dropdown_frame = ctk.CTkToplevel(self)
        self.dropdown_frame.withdraw()  # Hide initially
        self.dropdown_frame.overrideredirect(True)
        self.dropdown_frame.transient(self.winfo_toplevel())
        
        # Configure dropdown window
        self.dropdown_frame.configure(fg_color="#343638")
        
        # Create frame for options
        options_frame = ctk.CTkFrame(
            self.dropdown_frame,
            fg_color="transparent",
            corner_radius=8
        )
        options_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Add option buttons
        for value in self.values:
            btn = ctk.CTkButton(
                options_frame,
                text=value,
                fg_color="transparent",
                hover_color="#2B2B2B",
                anchor="w",
                height=32,
                corner_radius=6,
                command=lambda v=value: self.select_option(v)
            )
            btn.pack(fill="x", padx=2, pady=1)

        # Position dropdown below button
        self.update_dropdown_position()
        self.dropdown_frame.deiconify()  # Show after positioning
        
        # Bind events for tracking
        self.bind('<Configure>', self.update_dropdown_position)
        self.winfo_toplevel().bind('<Configure>', self.update_dropdown_position)
        self.master.bind('<Configure>', self.update_dropdown_position)
        
        # Bind scroll events from all parent widgets
        parent = self.master
        while parent:
            if isinstance(parent, ctk.CTkScrollableFrame):
                parent._scrollbar.bind('<B1-Motion>', self.update_dropdown_position)
                parent._scrollbar.bind('<ButtonRelease-1>', self.update_dropdown_position)
                parent.bind('<MouseWheel>', self.update_dropdown_position)
            parent = parent.master
            
        # Bind click events
        self.dropdown_frame.bind("<Button-1>", self.on_dropdown_click)
        self.winfo_toplevel().bind("<Button-1>", self.check_click_outside, add="+")

    def close_dropdown(self):
        """Close the dropdown"""
        if not self.is_open:
            return
            
        self.is_open = False
        
        # Unbind all events
        self.unbind('<Configure>')
        self.winfo_toplevel().unbind('<Configure>')
        self.master.unbind('<Configure>')
        
        # Unbind scroll events from all parent widgets
        parent = self.master
        while parent:
            if isinstance(parent, ctk.CTkScrollableFrame):
                parent._scrollbar.unbind('<B1-Motion>')
                parent._scrollbar.unbind('<ButtonRelease-1>')
                parent.unbind('<MouseWheel>')
            parent = parent.master
            
        # Unbind click events
        self.winfo_toplevel().unbind("<Button-1>")
        
        if self.dropdown_frame:
            self.dropdown_frame.destroy()
            self.dropdown_frame = None

    def update_dropdown_position(self, event=None):
        """Update the position of the dropdown to stay aligned with button"""
        if not self.dropdown_frame or not self.is_open:
            return
            
        # Get button position relative to screen
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        
        # Set dropdown position
        self.dropdown_frame.geometry(f"{self.winfo_width()}x{len(self.values) * 34}+{x}+{y}")
        self.dropdown_frame.lift()  # Ensure dropdown stays on top

    def select_option(self, value):
        """Select an option from the dropdown"""
        self.current_value = value
        self.main_button.configure(text=value + " ▾")
        self.close_dropdown()
        if self.command:
            self.command(value)

    def get(self):
        """Get the current value"""
        return self.current_value

    def set(self, value):
        """Set the current value"""
        if value in self.values:
            self.current_value = value
            self.main_button.configure(text=value + " ▾")

    def on_dropdown_click(self, event):
        """Handle clicks on the dropdown frame"""
        return "break"  # Prevent click from propagating

    def check_click_outside(self, event):
        """Check if click is outside dropdown and close if so"""
        if self.dropdown_frame:
            x, y = event.x_root, event.y_root
            frame_x = self.dropdown_frame.winfo_x()
            frame_y = self.dropdown_frame.winfo_y()
            frame_width = self.dropdown_frame.winfo_width()
            frame_height = self.dropdown_frame.winfo_height()
            
            if not (frame_x <= x <= frame_x + frame_width and 
                   frame_y <= y <= frame_y + frame_height):
                self.close_dropdown()
