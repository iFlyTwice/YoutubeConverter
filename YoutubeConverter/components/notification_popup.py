import customtkinter as ctk

class NotificationPopup(ctk.CTkToplevel):
    def __init__(self, *args, title="Notification", message="", primary_button="OK", secondary_button="Cancel", **kwargs):
        super().__init__(*args, **kwargs)
        
        # Window setup
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)
        
        # Make window float on top
        self.attributes('-topmost', True)
        
        # Center the window on screen
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')
        
        # Store the result
        self.result = None
        
        # Configure the grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")
        
        # Message
        self.message_label = ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(size=14),
            wraplength=360,
            justify="left"
        )
        self.message_label.grid(row=1, column=0, padx=20, pady=20, sticky="nw")
        
        # Buttons frame
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="e")
        
        # Secondary button (e.g., Cancel)
        if secondary_button:
            self.secondary_button = ctk.CTkButton(
                self.button_frame,
                text=secondary_button,
                width=100,
                fg_color="#2B2B2B",
                hover_color="#404040",
                command=self.handle_secondary
            )
            self.secondary_button.pack(side="left", padx=(0, 10))
        
        # Primary button (e.g., Save)
        self.primary_button = ctk.CTkButton(
            self.button_frame,
            text=primary_button,
            width=100,
            fg_color="#1f538d",
            hover_color="#1a4572",
            command=self.handle_primary
        )
        self.primary_button.pack(side="left")
        
        # Bind escape key to secondary action
        self.bind("<Escape>", lambda e: self.handle_secondary())
        
        # Bind enter key to primary action
        self.bind("<Return>", lambda e: self.handle_primary())
        
        # Make window modal
        self.transient(self.master)
        self.grab_set()
    
    def handle_primary(self):
        """Handle primary button click"""
        self.result = True
        self.destroy()
    
    def handle_secondary(self):
        """Handle secondary button click"""
        self.result = False
        self.destroy()
    
    @staticmethod
    def show_notification(master, title="Notification", message="", primary_button="OK", secondary_button="Cancel"):
        """Show a notification popup and return True if primary button was clicked"""
        popup = NotificationPopup(
            master,
            title=title,
            message=message,
            primary_button=primary_button,
            secondary_button=secondary_button
        )
        popup.wait_window()
        return popup.result
