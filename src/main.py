from pathlib import Path
import suborocess
import time
import re
import fastapi import FastAPI
from fastapi.middleware import BaseModel
import logging

logging.baseConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

#CORS middleware

app.middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DownloadRequest(BaseModel):
    url:str
    browser:str="chrome"

#directory where i want to download it

DONWLOAD_DIR = Path("/tmp/yt-downloads")
DONWLOAD_DIR.mkdir(parents=True,exist_ok=True)

#Regex to download the youtube video

YOUTUBE_REGEX = re.compile(r"^(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$")

@app.post("/api/download")
async def download_video(req: DownloadRequest):
    if not YOUTUBE_REGEX.match(req.url):
        return {"error":"Invalid Youtube URL"}
    
    filename = f"video_{int(time.time())}.mp4"
    output_path = str(DOWNLOAD_DIR / filename) 

    yt_dlp_cmd = [
        "yt-dlp",
        req.url,
        "--cookies-from-browser", req.browser,
        "-f", "ba",
        "--merge-output-format", "mp4",
        "--extractor-args", "youtube:player_client=android",
        "-o", output_path,
    ]

    try:
        result = subprocess.run(yt_dlp_cmd, check=True, capture_output=True, text=True)
        logger.info(result.stdout)
        return {
            "message": "Download successful",
            "fileUrl": f"/download-file/{filename}"
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Download failed: {e.stderr}")
        return {
            "error": "Download failed",
            "details": e.stderr if e.stderr else str(e)
        }
    except FileNotFoundError:
        return {
            "error": "yt-dlp not found. Please ensure it is installed and in your system's PATH."
        }
