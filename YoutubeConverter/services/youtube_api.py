import os
import logging
import yt_dlp
import json
from typing import Dict, Optional, Tuple, Callable
from utils.cookie_manager import cookie_manager

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
            'format': 'best',  # Get best quality
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1'
            },
            'socket_timeout': 30,
            'retries': 10,
            'file_access_retries': 5,
            'ignoreerrors': True,
            'no_check_certificate': True,
            'nocheckcertificate': True
        }

        # Try to get cookies from browser or file
        cookie_file = cookie_manager.get_cookies()
        if cookie_file:
            opts['cookiefile'] = cookie_file
            logging.info("Using cookie file for authentication")
        else:
            opts['cookiesfrombrowser'] = ('chrome', 'edge', 'firefox', 'opera', 'safari', 'brave')
            logging.info("Using browser cookies for authentication")

        return opts

    def get_video_metadata(self, video_id: str) -> Dict:
        """Get video metadata using yt-dlp with enhanced error handling"""
        logging.info(f"Fetching metadata for video ID: {video_id}")
        
        url = f"https://www.youtube.com/watch?v={video_id}"
        ydl_opts = self._get_yt_dlp_opts()
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    # First attempt with default options
                    info = ydl.extract_info(url, download=False)
                    if info:
                        return info
                except Exception as e:
                    logging.warning(f"First attempt failed: {str(e)}")
                    
                    # Second attempt with different user agent
                    ydl_opts['http_headers']['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'
                    ydl.params.update(ydl_opts)
                    try:
                        info = ydl.extract_info(url, download=False)
                        if info:
                            return info
                    except Exception as e2:
                        logging.error(f"Second attempt failed: {str(e2)}")
                        
                        # Third attempt with mobile user agent
                        ydl_opts['http_headers']['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1'
                        ydl.params.update(ydl_opts)
                        try:
                            info = ydl.extract_info(url, download=False)
                            return info
                        except Exception as e3:
                            logging.error(f"All attempts failed. Last error: {str(e3)}")
                            raise Exception("Failed to fetch video metadata after multiple attempts")
                            
        except Exception as e:
            logging.error(f"Error getting video info: {str(e)}")
            raise

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
            if any(msg in str(e).lower() for msg in ["sign in", "age", "confirm your age"]):
                logging.warning("Access restricted. Attempting with additional options...")
                # Clear and refresh cookies
                cookie_manager.clear_cookies()
                cookie_file = cookie_manager.get_cookies()
                if cookie_file:
                    ydl_opts['cookiefile'] = cookie_file
                    ydl_opts['age_limit'] = 21
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        return ydl.extract_info(url, download=download)
            raise

    def get_video_info(self, url: str) -> Optional[Dict]:
        """Get video information from URL"""
        try:
            info = self._extract_info(url)
            return {
                "id": info.get('id', ''),
                "title": info.get('title', 'Unknown Title'),
                "author": info.get('uploader', 'Unknown Channel'),
                "thumbnail_url": info.get('thumbnail', ''),
                "length": info.get('duration', 0),
                "views": info.get('view_count', 0),
                "published": info.get('upload_date', None)
            }
        except Exception as e:
            logging.error(f"Error getting video info: {e}")
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
                if any(msg in str(e).lower() for msg in ["sign in", "age", "confirm your age"]):
                    logging.warning("Access restricted. Attempting with additional options...")
                    # Clear and refresh cookies
                    cookie_manager.clear_cookies()
                    cookie_file = cookie_manager.get_cookies()
                    if cookie_file:
                        ydl_opts['cookiefile'] = cookie_file
                        ydl_opts['age_limit'] = 21
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
