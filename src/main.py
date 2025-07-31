from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import subprocess, re, os, time
from pathlib import Path
from fastapi.responses import FileResponse



app = FastAPI()
print("started working now")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
async def ping():
    return {"message": "pong"}


# Request body model
class DownloadRequest(BaseModel):
    url: str


DOWNLOAD_DIR = Path.home() / "Downloads"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/download-file/{filename}")
async def serve_file(filename: str):
    file_path = DOWNLOAD_DIR / filename
    if file_path.exists():
        return FileResponse(
            path=file_path,
            media_type='application/octet-stream',
            filename=filename
        )
    return {"error": "File not found"}


print("started working ")
print("This is official file location on your device",DOWNLOAD_DIR)

# YouTube URL regex
YOUTUBE_REGEX = re.compile(r"^(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+")

COOKIES_PATH = os.path.join(os.path.dirname(__file__), "youtube_cookies.txt")

@app.post("/api/download")
async def download_video(req: DownloadRequest):
    print("downloading the vdios")
    if not YOUTUBE_REGEX.match(req.url):
        return {"error": "Invalid YouTube URL"}

    filename = f"video_{int(time.time())}.%(ext)s"
    output_path = os.path.join(DOWNLOAD_DIR, filename)

    try:
        subprocess.run([
            "yt-dlp", req.url,
            "-o", output_path,
            "--cookies", COOKIES_PATH,
            "-f","b",
        ], check=True)

        return {
            "message": "Download successful",
            "fileUrl": f"/downloads/{filename}"
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
    output_path = os.path.join(DOWNLOAD_DIR, filename)

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
            "fileUrl": f"/downloads/{filename}"
        }

    except subprocess.CalledProcessError as e:
        return {
            "error": "Download failed",
            "details": str(e)
        }
