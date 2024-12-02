import json
import os

class SettingsManager:
    def __init__(self):
        self.settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'settings.json')
        self.default_settings = {
            'output_directory': os.path.join(os.path.expanduser('~'), 'Downloads'),
            'video_quality': 'Highest',
            'audio_format': 'MP3',
            'audio_quality': '320kbps',
            'theme': 'Dark',
            'always_on_top': False
        }
        self.ensure_settings_file()
        
    def ensure_settings_file(self):
        """Create settings file and directory if they don't exist"""
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        if not os.path.exists(self.settings_file):
            self.save_settings(self.default_settings)
    
    def load_settings(self):
        """Load settings from file"""
        try:
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self.default_settings.copy()
    
    def save_settings(self, settings):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get_setting(self, key, default=None):
        """Get a specific setting value"""
        settings = self.load_settings()
        return settings.get(key, default or self.default_settings.get(key))
    
    def update_setting(self, key, value):
        """Update a specific setting"""
        settings = self.load_settings()
        settings[key] = value
        return self.save_settings(settings)
    
    def update_settings(self, new_settings):
        """Update multiple settings at once"""
        settings = self.load_settings()
        settings.update(new_settings)
        return self.save_settings(settings)
