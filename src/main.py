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

COOKIES_FILE = Path(__file__).resolve().parent.parent / "cookies.txt"


YOUTUBE_REGEX = re.compile(r"^(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$")

@app.post("/api/download")
async def download_video(req: DownloadRequest):
    if not YOUTUBE_REGEX.match(req.url):
        return {"error": "Invalid YouTube URL"}

    filename = f"video_{int(time.time())}.mp4"
    output_path = str(DOWNLOAD_DIR / filename)

    if not COOKIES_FILE.exists():
        return {"error": "cookies.txt not found. Please upload valid cookies."}

    yt_dlp_cmd = [
        "yt-dlp",
        req.url,
        "--cookies", COOKIES_FILE,
        "-f", "bestvideo+bestaudio",
        "--merge-output-format", "mp4",
        "--extractor-args", "youtube:player_client=android",
        "-o", output_path,
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
            "details": e.stderr if e.stderr else str(e)
        }
