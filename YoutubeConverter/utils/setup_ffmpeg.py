import os
import requests
import zipfile
from pathlib import Path
import shutil
import sys

def download_ffmpeg():
    """Download and set up ffmpeg for Windows"""
    try:
        # Create ffmpeg directory
        ffmpeg_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ffmpeg')
        os.makedirs(ffmpeg_dir, exist_ok=True)
        
        # Download ffmpeg
        url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        print("Downloading ffmpeg...")
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        zip_path = os.path.join(ffmpeg_dir, "ffmpeg.zip")
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Extract ffmpeg
        print("Extracting ffmpeg...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(ffmpeg_dir)
        
        # Move ffmpeg executables to bin directory
        bin_dir = os.path.join(ffmpeg_dir, 'bin')
        os.makedirs(bin_dir, exist_ok=True)
        
        extracted_dir = next(Path(ffmpeg_dir).glob('ffmpeg-master-*'))
        for exe in ['ffmpeg.exe', 'ffprobe.exe']:
            src = os.path.join(extracted_dir, 'bin', exe)
            dst = os.path.join(bin_dir, exe)
            shutil.move(src, dst)
        
        # Clean up
        os.remove(zip_path)
        shutil.rmtree(str(extracted_dir))
        
        # Add to PATH
        ffmpeg_bin = os.path.abspath(bin_dir)
        if ffmpeg_bin not in os.environ['PATH']:
            os.environ['PATH'] = ffmpeg_bin + os.pathsep + os.environ['PATH']
        
        print("ffmpeg setup complete!")
        return True
        
    except Exception as e:
        print(f"Error setting up ffmpeg: {e}")
        return False

if __name__ == "__main__":
    download_ffmpeg()
