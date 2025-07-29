from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import subprocess, re, os, time
from pathlib import Path

from fastapi import BackgroundTasks
from fastapi.responses import FileResponse

def delete_file(path: str):
    if os.path.exists(path):
        os.remove(path)



app = FastAPI()
print("started working now")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body model
class DownloadRequest(BaseModel):
    url: str


DOWNLOAD_DIR = Path.home() / "Downloads"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/downloads", StaticFiles(directory=str(DOWNLOAD_DIR)), name="downloads")
print("This is official file location on your device",DOWNLOAD_DIR)

# YouTube URL regex
YOUTUBE_REGEX = re.compile(r"^(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+")

app.get("/")
async def read_root():
    return {
        "message":"Welcome to tubesave BACKEND API is working very fine "
    }

@app.post("/api/download")
async def download_video(req: DownloadRequest, background_tasks: BackgroundTasks):
    if not YOUTUBE_REGEX.match(req.url):
        return {"error": "Invalid YouTube URL"}

    filename = f"video_{int(time.time())}.mp4"
    output_path = os.path.join(DOWNLOAD_DIR, filename)

    try:
        subprocess.run([
            "yt-dlp",
            req.url,
            "-f", "bestvideo+bestaudio/best",
            "-o", output_path,
            "--no-check-certificate",
            "--no-warnings",
            "--add-header", "referer:youtube.com",
            "--add-header", "user-agent:googlebot"
        ], check=True)

        background_tasks.add_task(delete_file, output_path)

        return FileResponse(
            output_path,
            media_type="video/mp4",
            filename=filename,
        )

    except subprocess.CalledProcessError as e:
        return {
            "error": "Download failed",
            "details": str(e)
        }


@app.post("/api/downloadMp3")
async def download_audio(req: DownloadRequest, background_tasks: BackgroundTasks):
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

        background_tasks.add_task(delete_file, output_path)

        return FileResponse(
            output_path,
            media_type="audio/mpeg",
            filename=filename,
        )

    except subprocess.CalledProcessError as e:
        return {
            "error": "Download failed",
            "details": str(e)
        }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
