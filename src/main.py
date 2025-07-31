from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import subprocess, re, os, time
from pathlib import Path

app = FastAPI()

# CORS
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

# Model
class DownloadRequest(BaseModel):
    url: str

# Use /tmp/yt-downloads
DOWNLOAD_DIR = Path("/tmp/yt-downloads")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/download-file/{filename}")
async def serve_file(filename: str):
    file_path = DOWNLOAD_DIR / filename
    if file_path.exists():
        return FileResponse(
            path=file_path,
            media_type='application/octet-stream',
            filename=filename,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    return Response(content='{"error": "File not found"}', media_type="application/json", status_code=404)

YOUTUBE_REGEX = re.compile(r"^(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+")

@app.post("/api/download")
async def download_video(req: DownloadRequest):
    if not YOUTUBE_REGEX.match(req.url):
        return {"error": "Invalid YouTube URL"}

    filename = f"video_{int(time.time())}.mp4"
    output_path = str(DOWNLOAD_DIR / filename)

    try:
        subprocess.run([
            "yt-dlp", req.url,
            "--cookies", "cookies.txt"
            "-o", output_path,
            "-f", "b"
        ], check=True)

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
