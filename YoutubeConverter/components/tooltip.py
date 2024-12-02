import customtkinter as ctk
import tkinter as tk

class ModernTooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self._destroyed = False
        self._schedule_id = None
        
        # Modern tooltip colors
        self.BG_COLOR = "#2B2B2B"        # Darker background
        self.BORDER_COLOR = "#3F3F3F"    # Subtle border
        self.TEXT_COLOR = "#E0E0E0"      # Light gray text
        self.SHADOW_COLOR = "#1A1A1A"    # Shadow color
        
        self.widget.bind("<Enter>", self.on_enter, add="+")
        self.widget.bind("<Leave>", self.on_leave, add="+")
        self.widget.bind("<Button-1>", self.hide_tooltip, add="+")
        self.widget.bind("<Destroy>", lambda e: self.cleanup(), add="+")

    def cleanup(self):
        self._destroyed = True
        if self._schedule_id:
            self.widget.after_cancel(self._schedule_id)
            self._schedule_id = None
        if self.tooltip_window:
            try:
                self.tooltip_window.destroy()
            except:
                pass
            self.tooltip_window = None

    def on_enter(self, event=None):
        self._destroyed = False
        self._schedule_id = self.widget.after(400, self.show_tooltip)

    def on_leave(self, event=None):
        if self._schedule_id:
            self.widget.after_cancel(self._schedule_id)
            self._schedule_id = None
        self.hide_tooltip()

    def show_tooltip(self):
        if self._destroyed or self.tooltip_window:
            return

        try:
            x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8

            # Create main tooltip window
            self.tooltip_window = tw = tk.Toplevel()
            tw.withdraw()
            tw.wm_overrideredirect(True)
            
            # Create shadow window
            shadow = tk.Toplevel(tw)
            shadow.withdraw()
            shadow.wm_overrideredirect(True)
            shadow.configure(bg=self.SHADOW_COLOR)
            
            # Main tooltip frame with modern design
            frame = tk.Frame(
                tw,
                bg=self.BG_COLOR,
                highlightthickness=1,
                highlightbackground=self.BORDER_COLOR,
                highlightcolor=self.BORDER_COLOR
            )
            frame.pack(padx=0, pady=0)
            
            # Modern label with custom font
            label = tk.Label(
                frame,
                text=self.text,
                fg=self.TEXT_COLOR,
                bg=self.BG_COLOR,
                font=("Segoe UI", 11),
                padx=12,
                pady=6,
                justify=tk.LEFT
            )
            label.pack()

            # Position the tooltip
            tw.update_idletasks()
            tooltip_width = tw.winfo_width()
            tooltip_height = tw.winfo_height()
            x -= tooltip_width // 2
            
            # Position shadow slightly offset
            shadow.geometry(f"{tooltip_width}x{tooltip_height}+{x+2}+{y+2}")
            shadow.attributes('-alpha', 0.2)  # Semi-transparent shadow
            shadow.lift()
            shadow.deiconify()
            
            # Position main tooltip
            tw.wm_geometry(f"+{x}+{y}")
            tw.lift()
            tw.attributes('-topmost', True)
            tw.deiconify()
            
        except:
            self.cleanup()

    def hide_tooltip(self, event=None):
        if not self._destroyed and self.tooltip_window:
            self.cleanup()
