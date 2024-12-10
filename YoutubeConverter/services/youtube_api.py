import os
import logging
import yt_dlp
import json
from typing import Dict, Optional, Tuple, Callable
from utils.cookie_manager import cookie_manager
from utils.browser_automation import BrowserAutomation

class YouTubeAPI:
    def __init__(self) -> None:
        """Initialize YouTubeAPI with settings.json."""
        settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'settings.json')
        self.api_key: Optional[str] = None
        try:
            with open(settings_path, 'r') as f:
                settings = json.load(f)
                self.api_key = settings.get('youtube_api_key')
        except FileNotFoundError:
            logging.warning(f"Settings file not found at {settings_path}.")
        except json.JSONDecodeError as e:
            logging.warning(f"Error decoding settings file: {e}")
        except Exception as e:
            logging.warning(f"Unexpected error loading settings: {e}")

    def _get_yt_dlp_opts(self, download: bool = False) -> Dict:
        """Get common yt-dlp options with proper cookie handling."""
        opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': not download,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            },
            'socket_timeout': 30,
            'retries': 10,
            'file_access_retries': 5,
            'age_limit': 21,  # Always set age limit to handle age-restricted videos
        }

        # Always try to use cookie file first
        cookie_file = cookie_manager.get_cookies()
        if cookie_file and os.path.exists(cookie_file) and os.path.getsize(cookie_file) > 100:
            opts['cookiefile'] = cookie_file
        else:
            # If no valid cookie file, try browser cookies as fallback
            opts['cookiesfrombrowser'] = ('chrome', 'firefox', 'edge')

        return opts

    def get_video_metadata(self, video_id: str) -> Dict:
        """Get video metadata using yt-dlp"""
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            return self._extract_info(url)
        except Exception as e:
            logging.error(f"Error getting video metadata: {e}")
            return self._get_fallback_data(video_id)

    def _get_fallback_data(self, video_id: str) -> Dict:
        """Fallback data when API fails"""
        return {
            "id": video_id,
            "title": "Video Title Unavailable",
            "author": "Channel Unavailable",
            "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
            "length": 0,
            "views": 0,
            "published": None
        }

    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL using yt-dlp"""
        try:
            info = self._extract_info(url)
            return info.get('id')
        except Exception as e:
            logging.error(f"Error extracting video ID: {e}")
            return None

    def _extract_info(self, url: str, download: bool = False) -> Dict:
        """Extract video information using yt-dlp."""
        ydl_opts = self._get_yt_dlp_opts(download)
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=download)
        except yt_dlp.utils.ExtractorError as e:
            error_msg = str(e).lower()
            if any(msg in error_msg for msg in ["sign in", "age", "confirm your age", "bot"]):
                logging.warning("Access restricted or bot detection. Clearing cookies and retrying...")
                # Clear cookies to force refresh
                cookie_manager.clear_cookies()
                # Retry with fresh options
                ydl_opts = self._get_yt_dlp_opts(download)
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    return ydl.extract_info(url, download=download)
            raise

    def _load_auth_info(self) -> tuple[str, str]:
        """Load authentication information from JSON file"""
        try:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
            auth_file = os.path.join(data_dir, 'youtube_auth.json')
            
            if not os.path.exists(auth_file):
                logging.warning("No authentication file found")
                return None, None
                
            with open(auth_file, 'r', encoding='utf-8') as f:
                auth_data = json.load(f)
                
            return auth_data.get('cookies'), auth_data.get('visitor_data')
        except Exception as e:
            logging.error(f"Error loading authentication information: {e}")
            return None, None

    def _parse_cookies_to_dict(self, cookies_str: str) -> dict:
        """Convert cookie string to dictionary format"""
        try:
            cookies_dict = {}
            for line in cookies_str.split('\n'):
                if line and not line.startswith('#'):
                    fields = line.split('\t')
                    if len(fields) >= 7:
                        name = fields[5]
                        value = fields[6]
                        cookies_dict[name] = value
            return cookies_dict
        except Exception as e:
            logging.error(f"Error parsing cookies: {e}")
            return {}

    def _save_temp_cookies(self, cookies: str) -> str:
        """Save cookies to a temporary file and return the path"""
        try:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
            os.makedirs(data_dir, exist_ok=True)
            cookie_file = os.path.join(data_dir, 'temp_cookies.txt')
            
            # Add Netscape format header
            cookie_content = "# Netscape HTTP Cookie File\n"
            cookie_content += "# https://curl.haxx.se/rfc/cookie_spec.html\n"
            cookie_content += "# This is a generated file!  Do not edit.\n\n"
            cookie_content += cookies
            
            with open(cookie_file, 'w', encoding='utf-8') as f:
                f.write(cookie_content)
            
            return cookie_file
        except Exception as e:
            logging.error(f"Error saving temporary cookies: {e}")
            return None

    def get_video_info(self, url: str) -> Optional[Dict]:
        """Get video information from URL"""
        try:
            logging.info(f"Starting to fetch video info for URL: {url}")
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'dump_single_json': True,  # Just get metadata as JSON
                'skip_download': True,
                'no_playlist': True,
                'extract_flat': True,
                'format': None,
                'force_generic_extractor': False,
                'ignoreerrors': True,
            }

            # Try to get cookies from cookie manager
            cookie_file = cookie_manager.get_cookies()
            if cookie_file and os.path.exists(cookie_file):
                logging.info(f"Using cookie file: {cookie_file}")
                ydl_opts['cookiefile'] = cookie_file
            else:
                logging.info("No cookie file found, using browser cookies")
                ydl_opts['cookiesfrombrowser'] = ('chrome',)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logging.info("Extracting video info...")
                try:
                    # First try to just extract the video ID and basic info
                    basic_info = ydl.extract_info(url, download=False, process=False)
                    logging.info(f"Basic info extracted: {basic_info}")
                    
                    if basic_info:
                        video_info = {
                            'title': basic_info.get('title', 'Unknown Title'),
                            'author': basic_info.get('uploader', basic_info.get('channel', 'Unknown Channel')),
                            'duration': basic_info.get('duration', 0),
                            'thumbnail': basic_info.get('thumbnail', '')
                        }
                        
                        # If no thumbnail, try to get it from video ID
                        if not video_info['thumbnail'] and basic_info.get('id'):
                            video_info['thumbnail'] = f"https://img.youtube.com/vi/{basic_info['id']}/maxresdefault.jpg"
                        
                        logging.info(f"Successfully extracted video info: {video_info}")
                        return video_info
                    else:
                        logging.error("No basic info found")
                        return None
                        
                except yt_dlp.utils.ExtractorError as e:
                    if any(msg in str(e).lower() for msg in ["sign in", "age", "confirm your age", "bot"]):
                        logging.warning("Access restricted or bot detection. Clearing cookies and retrying...")
                        cookie_manager.clear_cookies()
                        ydl_opts['cookiesfrombrowser'] = ('chrome',)
                        basic_info = ydl.extract_info(url, download=False, process=False)
                        if basic_info:
                            video_info = {
                                'title': basic_info.get('title', 'Unknown Title'),
                                'author': basic_info.get('uploader', basic_info.get('channel', 'Unknown Channel')),
                                'duration': basic_info.get('duration', 0),
                                'thumbnail': basic_info.get('thumbnail', '')
                            }
                            if not video_info['thumbnail'] and basic_info.get('id'):
                                video_info['thumbnail'] = f"https://img.youtube.com/vi/{basic_info['id']}/maxresdefault.jpg"
                            return video_info
                    raise

        except Exception as e:
            logging.error(f"Error getting video info: {str(e)}")
            logging.error(f"Error type: {type(e)}")
            logging.error(f"Error details: {str(e)}")
            return None

    def validate_url(self, url: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """Validate YouTube URL and get video info"""
        try:
            if not url or not isinstance(url, str):
                raise ValueError("Invalid URL format")

            info = self.get_video_info(url)
            if not info or not info.get("title"):
                raise ValueError("Could not retrieve video information")
            
            return True, info, None

        except Exception as e:
            return False, None, str(e)

    def _configure_download(self, format: str, quality: str) -> Tuple[str, list]:
        """Configure format based on quality and format type"""
        if format.lower() == 'mp3':
            format_str = 'bestaudio/best'
            postprocessors = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }]
        else:
            if quality.lower() in ['best', 'highest']:
                format_str = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            else:
                height = quality.replace('p', '')
                format_str = f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={height}][ext=mp4]/best'
            postprocessors = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }]
        return format_str, postprocessors

    def download_video(
        self,
        url: str,
        output_path: str,
        format: str = 'mp4',
        quality: str = 'best',
        progress_callback: Optional[Callable[[float], None]] = None,
    ) -> str:
        """Download video using yt-dlp with an optional progress callback."""
        try:
            os.makedirs(output_path, exist_ok=True)
            format_str, postprocessors = self._configure_download(format, quality)

            def progress_hook(d):
                if d['status'] == 'downloading' and progress_callback:
                    try:
                        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                        downloaded = d.get('downloaded_bytes', 0)
                        if total_bytes:
                            progress = (downloaded / total_bytes) * 100
                            progress_callback(progress)
                    except Exception as e:
                        logging.error(f"Error in progress callback: {e}")

            ydl_opts = self._get_yt_dlp_opts(download=True)
            ydl_opts.update({
                'format': format_str,
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [progress_hook],
                'postprocessors': postprocessors,
                'merge_output_format': 'mp4',
                'sleep_interval': 1,
                'max_sleep_interval': 5,
                'ignoreerrors': True,
                'fragment_retries': 10,
            })

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    if not info:
                        raise Exception("Failed to download video")
                    ext = "mp3" if format.lower() == "mp3" else "mp4"
                    return os.path.join(output_path, f"{info['title']}.{ext}")
            except yt_dlp.utils.ExtractorError as e:
                if any(msg in str(e).lower() for msg in ["sign in", "age", "confirm your age", "bot"]):
                    logging.warning("Access restricted or bot detection. Clearing cookies and retrying...")
                    # Clear cookies to force refresh
                    cookie_manager.clear_cookies()
                    # Retry with fresh options
                    ydl_opts = self._get_yt_dlp_opts(download=True)
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        if not info:
                            raise Exception("Failed to download video")
                        ext = "mp3" if format.lower() == "mp3" else "mp4"
                        return os.path.join(output_path, f"{info['title']}.{ext}")
                raise

        except Exception as e:
            logging.error(f"Error downloading video from URL: {url}, error: {e}")
            raise

# Global instance
api = YouTubeAPI()
