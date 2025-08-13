import subprocess
import re
import os
import time
from pathlib import Path

DOWNLOAD_DIR = Path("./yt-downloads")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

YOUTUBE_REGEX = re.compile(r"^(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+")

def download_video(url: str):
    """Download a YouTube video as MP4."""
    if not YOUTUBE_REGEX.match(url):
        print(" Invalid YouTube URL.")
        return

    filename = f"video_{int(time.time())}.mp4"
    output_path = str(DOWNLOAD_DIR / filename)

    try:
        subprocess.run([
            "yt-dlp", url,
            "-o", output_path,
            "-f", "b"
        ], check=True)
        print(f" Video downloaded successfully: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f" Download failed: {e}")

def download_audio(url: str):
    """Download a YouTube video as MP3."""
    if not YOUTUBE_REGEX.match(url):
        print(" Invalid YouTube URL.")
        return

    filename = f"audio_{int(time.time())}.mp3"
    output_path = str(DOWNLOAD_DIR / filename)

    try:
        subprocess.run([
            "yt-dlp",
            "-x",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "-o", output_path,
            url
        ], check=True)
        print(f"Audio downloaded successfully: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f" Download failed: {e}")

if __name__ == "__main__":
    print("🎵 YouTube Downloader")
    url = input("Enter YouTube URL: ").strip()
    mode = input("Download as video (mp4) or audio (mp3)? [video/audio]: ").strip().lower()

    if mode == "video":
        download_video(url)
    elif mode == "audio":
        download_audio(url)
    else:
        print(" Invalid option. Choose 'video' or 'audio'.")
