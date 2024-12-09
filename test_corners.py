import customtkinter as ctk

class TestWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Test Corner Radius")
        self.geometry("400x500")
        
        # Configure for light theme to see the corner issue
        self.configure(fg_color="white")
        
        # Create content frame
        content = ctk.CTkScrollableFrame(self, fg_color="white")
        content.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Label for first separator (with default corner radius)
        label1 = ctk.CTkLabel(content, text="Separator with default corner radius:", text_color="black")
        label1.pack(pady=(10,5))
        
        # First separator (with default corner radius)
        separator1 = ctk.CTkFrame(
            content,
            height=2,
            fg_color="#3d3d3d"
        )
        separator1.pack(fill="x", pady=8, padx=15)
        
        # Some space between separators
        spacing = ctk.CTkFrame(content, height=40, fg_color="transparent")
        spacing.pack()
        
        # Label for second separator (with corner_radius=0)
        label2 = ctk.CTkLabel(content, text="Separator with corner_radius=0:", text_color="black")
        label2.pack(pady=(10,5))
        
        # Second separator (with corner_radius=0)
        separator2 = ctk.CTkFrame(
            content,
            height=2,
            fg_color="#3d3d3d",
            corner_radius=0
        )
        separator2.pack(fill="x", pady=8, padx=15)

if __name__ == "__main__":
    app = TestWindow()
    app.mainloop()
