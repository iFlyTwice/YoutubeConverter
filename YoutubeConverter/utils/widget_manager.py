import logging
from typing import Optional
import tkinter as tk
import customtkinter as ctk
from threading import Lock

class WidgetManager:
    def __init__(self):
        self.widgets = {}
        self.lock = Lock()
        
    def register(self, widget: tk.Widget, parent_id: Optional[str] = None):
        """Register a widget and its parent"""
        with self.lock:
            widget_id = str(widget)
            self.widgets[widget_id] = {
                "widget": widget,
                "parent": parent_id,
                "children": set()
            }
            if parent_id and parent_id in self.widgets:
                self.widgets[parent_id]["children"].add(widget_id)
    
    def unregister(self, widget: tk.Widget):
        """Unregister a widget and its children"""
        with self.lock:
            widget_id = str(widget)
            if widget_id in self.widgets:
                # First unregister children
                children = list(self.widgets[widget_id]["children"])
                for child_id in children:
                    if child_id in self.widgets:
                        child_widget = self.widgets[child_id]["widget"]
                        self.unregister(child_widget)
                
                # Remove from parent's children set
                parent_id = self.widgets[widget_id]["parent"]
                if parent_id and parent_id in self.widgets:
                    self.widgets[parent_id]["children"].discard(widget_id)
                
                # Remove this widget
                del self.widgets[widget_id]
    
    def safe_destroy(self, widget: tk.Widget):
        """Safely destroy a widget and its children"""
        try:
            if not widget.winfo_exists():
                return
            
            # Unregister before destroying
            self.unregister(widget)
            
            # Destroy the widget
            widget.destroy()
            
        except Exception as e:
            logging.error(f"Error destroying widget: {e}")
    
    def create_managed_widget(self, widget_class, parent, **kwargs):
        """Create a widget that's automatically managed"""
        widget = widget_class(parent, **kwargs)
        self.register(widget, str(parent))
        return widget

# Global instance
manager = WidgetManager()
