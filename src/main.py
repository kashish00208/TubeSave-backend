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

COOKIES_FILE = Path(__file__).resolve().parent / "cookies.txt"

YOUTUBE_REGEX = re.compile(r"^(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$")

def run_yt_dlp(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result

@app.post("/api/download")
async def download_video(req: DownloadRequest):
    if not YOUTUBE_REGEX.match(req.url):
        return {"error": "Invalid YouTube URL"}

    filename = f"video_{int(time.time())}.mp4"
    output_path = str(DOWNLOAD_DIR / filename)

    cmd_no_cookies = [
        "yt-dlp",
        "--extractor-args", "youtube:player_client=ios",
        "-f", "b",
        "-o", output_path,
        req.url
    ]

    res = run_yt_dlp(cmd_no_cookies)

    if res.returncode == 0:
        return {"message": "Download successful (no cookies)", "fileUrl": f"/download-file/{filename}"}

    if "Sign in to confirm you’re not a bot" in res.stderr and COOKIES_FILE.exists():
        cmd_with_cookies = [
            "yt-dlp",
            "--cookies", str(COOKIES_FILE),
            "-f", "b",
            "-o", output_path,
            req.url
        ]
        res_cookies = run_yt_dlp(cmd_with_cookies)

        if res_cookies.returncode == 0:
            return {"message": "Download successful (with cookies)", "fileUrl": f"/download-file/{filename}"}
        else:
            return {"error": "Download failed even with cookies", "details": res_cookies.stderr}

    return {"error": "Download failed", "details": res.stderr}
