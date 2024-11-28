import os
import json
import logging
from typing import Optional, Dict
from pathlib import Path

class CookieManager:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.cookie_file = os.path.join(self.data_dir, 'cookies.txt')
        os.makedirs(self.data_dir, exist_ok=True)

    def get_cookies(self) -> Optional[str]:
        """Get cookie file path if it exists."""
        if os.path.exists(self.cookie_file):
            return self.cookie_file
        else:
            self._create_empty_cookie_file()
            return self.cookie_file

    def _create_empty_cookie_file(self) -> None:
        """Create an empty Netscape-format cookies file."""
        try:
            with open(self.cookie_file, 'w', encoding='utf-8') as f:
                f.write("# Netscape HTTP Cookie File\n")
                f.write("# https://curl.haxx.se/rfc/cookie_spec.html\n")
                f.write("# This is a generated file!  Do not edit.\n\n")
            logging.info(f"Created empty cookie file at {self.cookie_file}")
        except Exception as e:
            logging.error(f"Error creating cookie file: {e}")

    def clear_cookies(self) -> bool:
        """Clear saved cookies."""
        try:
            if os.path.exists(self.cookie_file):
                os.remove(self.cookie_file)
            self._create_empty_cookie_file()
            return True
        except Exception as e:
            logging.error(f"Error clearing cookies: {e}")
            return False

# Global instance
cookie_manager = CookieManager()
