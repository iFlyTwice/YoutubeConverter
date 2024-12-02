import customtkinter as ctk
from .tooltip import ModernTooltip

class AnimatedButton(ctk.CTkButton):
    def __init__(self, *args, tooltip_text="", **kwargs):
        self.hover_color = kwargs.pop('hover_color', '#505050')
        self.original_color = kwargs.get('fg_color', '#404040')
        super().__init__(*args, **kwargs)
        
        if tooltip_text:
            self.tooltip = ModernTooltip(self, tooltip_text)
        
        self.bind("<Enter>", self.on_enter, add="+")
        self.bind("<Leave>", self.on_leave, add="+")

    def on_enter(self, event):
        self.configure(fg_color=self.hover_color)

    def on_leave(self, event):
        self.configure(fg_color=self.original_color)

class HamburgerButton(AnimatedButton):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            text="☰",
            width=40,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=20, weight="bold"),
            tooltip_text="Menu Options",
            **kwargs
        )
