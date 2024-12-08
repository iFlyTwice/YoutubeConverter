class Sidebar:
    def __init__(self):
        self.is_visible = True
        self._active_item = 'Home'
        self._focused_item = 'Home'
        self._theme = 'light'
        self._navigation_callback = None
        self._navigation_items = [
            {
                'name': 'Home',
                'icon': 'home',
                'aria-label': 'Navigate to Home page'
            },
            {
                'name': 'Downloads',
                'icon': 'download',
                'aria-label': 'View Downloads'
            },
            {
                'name': 'Settings',
                'icon': 'settings',
                'aria-label': 'Open Settings'
            }
        ]

    def toggle(self):
        """Toggle sidebar visibility."""
        self.is_visible = not self.is_visible

    def get_navigation_items(self):
        """Get all navigation items."""
        return self._navigation_items

    def set_active_item(self, item_name):
        """Set the active navigation item."""
        if not any(item['name'] == item_name for item in self._navigation_items):
            raise ValueError(f"Invalid navigation item: {item_name}")
        self._active_item = item_name

    def get_active_item(self):
        """Get the currently active item."""
        return self._active_item

    def set_navigation_callback(self, callback):
        """Set callback for navigation events."""
        self._navigation_callback = callback

    def navigate_to(self, item_name):
        """Navigate to a specific item."""
        self.set_active_item(item_name)
        if self._navigation_callback:
            self._navigation_callback(item_name)
        self._handle_navigation(item_name)

    def _handle_navigation(self, item_name):
        """Internal navigation handler."""
        pass  # Implementation will be added later

    def get_current_theme(self):
        """Get current theme."""
        return self._theme

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self._theme = 'dark' if self._theme == 'light' else 'light'

    def set_theme(self, theme):
        """Set specific theme."""
        if theme not in ['light', 'dark']:
            raise ValueError("Theme must be either 'light' or 'dark'")
        self._theme = theme

    def get_theme_styles(self):
        """Get theme-specific styles."""
        return {
            'background': 'white' if self._theme == 'light' else 'dark',
            'text': 'black' if self._theme == 'light' else 'white'
        }

    def handle_keyboard_navigation(self, direction):
        """Handle keyboard navigation."""
        current_index = next(
            (i for i, item in enumerate(self._navigation_items) 
             if item['name'] == self._focused_item), 0
        )
        
        if direction == 'down':
            new_index = (current_index + 1) % len(self._navigation_items)
        else:  # up
            new_index = (current_index - 1) % len(self._navigation_items)
            
        self._focused_item = self._navigation_items[new_index]['name']

    def get_focused_item(self):
        """Get currently focused item."""
        return self._focused_item

    def save_state(self):
        """Save current sidebar state."""
        return {
            'is_visible': self.is_visible,
            'active_item': self._active_item,
            'theme': self._theme
        }

    def load_state(self, state):
        """Load saved sidebar state."""
        self.is_visible = state.get('is_visible', True)
        self._active_item = state.get('active_item', 'Home')
        self._theme = state.get('theme', 'light')
