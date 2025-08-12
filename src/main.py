from pathlib import Path
import subprocess
import time
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DownloadRequest(BaseModel):
    url: str

DOWNLOAD_DIR = Path("/tmp/yt-downloads")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Path to cookies.txt (next to this file or in your repo)
COOKIES_FILE = Path(__file__).resolve().parent / "cookies.txt"

YOUTUBE_REGEX = re.compile(r"^(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$")

@app.post("/api/download")
async def download_video(req: DownloadRequest):
    if not YOUTUBE_REGEX.match(req.url):
        return {"error": "Invalid YouTube URL"}

    filename = f"video_{int(time.time())}.mp4"
    output_path = str(DOWNLOAD_DIR / filename)

    # Build yt-dlp command
    if COOKIES_FILE.exists():
        yt_dlp_cmd = [
            "yt-dlp", "--cookies", str(COOKIES_FILE),
            "-o", output_path,
            "-f", "b",
            req.url
        ]
    else:
        # Local dev fallback (only works locally, not on Render)
        yt_dlp_cmd = [
            "yt-dlp", "--cookies-from-browser", "chrome",
            "-o", output_path,
            "-f", "b",
            req.url
        ]

    try:
        subprocess.run(yt_dlp_cmd, check=True)
        return {
            "message": "Download successful",
            "fileUrl": f"/download-file/{filename}"
        }
    except subprocess.CalledProcessError as e:
        return {
            "error": "Download failed",
            "details": str(e)
        }


@app.post("/api/downloadMp3")
async def download_audio(req: DownloadRequest):
    if not YOUTUBE_REGEX.match(req.url):
        return {"error": "Invalid YouTube URL"}

    filename = f"audio_{int(time.time())}.mp3"
    output_path = str(DOWNLOAD_DIR / filename)

    try:
        subprocess.run([
            "yt-dlp",
            "-x",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "-o", output_path,
            req.url
        ], check=True)

        return {
            "message": "Audio downloaded successfully",
            "fileUrl": f"/download-file/{filename}"
        }

    except subprocess.CalledProcessError as e:
        return {
            "error": "Download failed",
            "details": str(e)
        }
