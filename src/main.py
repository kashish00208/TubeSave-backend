from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import subprocess, re, os, time
from pathlib import Path
import tempfile


app = FastAPI()
print("Server started...")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
async def ping():
    return {"message": "pong"}

# Input schema
class DownloadRequest(BaseModel):
    url: str

# ⛱ Use temporary directory for storing files
DOWNLOAD_DIR = Path(tempfile.gettempdir()) / "yt-dlp-files"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
print("Download location:", DOWNLOAD_DIR)

#  Regex to check valid YouTube URL
YOUTUBE_REGEX = re.compile(r"^(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+")

# Optional cookies.txt path
COOKIES_PATH = os.path.join(os.path.dirname(__file__), "cookies.txt")


@app.post("/api/download")
async def download_video(req: DownloadRequest):
    print("Requested download for:", req.url)

    if not YOUTUBE_REGEX.match(req.url):
        return JSONResponse(content={"error": "Invalid YouTube URL"}, status_code=400)

    filename = f"video_{int(time.time())}.mp4"
    output_path = DOWNLOAD_DIR / filename

    try:
        subprocess.run([
            "yt-dlp", req.url,
            "--cookies", COOKIES_PATH,
            "-f", "best", 
            "-o", str(output_path)
        ], check=True)

        return {
            "message": "Download successful",
            "filePath": str(output_path)  
        }

    except subprocess.CalledProcessError as e:
        return {
            "error": "Download failed",
            "details": str(e)
        }


@app.post("/api/downloadMp3")
async def download_audio(req: DownloadRequest):
    if not YOUTUBE_REGEX.match(req.url):
        return JSONResponse(content={"error": "Invalid YouTube URL"}, status_code=400)

    filename = f"audio_{int(time.time())}.mp3"
    output_path = DOWNLOAD_DIR / filename

    try:
        subprocess.run([
            "yt-dlp",
            "-x",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "--cookies", COOKIES_PATH,
            "-o", str(output_path),
            req.url
        ], check=True)

        return {
            "message": "Audio downloaded successfully",
            "filePath": str(output_path)
        }

    except subprocess.CalledProcessError as e:
        return {
            "error": "Download failed",
            "details": str(e)
        }
