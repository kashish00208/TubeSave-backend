import os
from pathlib import Path
import subprocess
import time
import re
import logging
from typing import Dict
from dotenv import load_dotenv

# FastAPI imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Selenium imports 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
YOUTUBE_COOKIES: Dict[str, str] = {}
YOUTUBE_REGEX = re.compile(r"^(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$")

# Selenium setup for the headless browser
def setup_headless_browser():
    """Sets up and returns a headless Chrome browser instance."""
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Use webdriver-manager to automatically handle the correct chromedriver version
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Function to get fresh cookies from YouTube
def get_youtube_cookies(username: str, password: str) -> Dict[str, str]:
    """
    Automates a login to YouTube and extracts the session cookies.
    """
    logger.info("Starting headless browser to get fresh YouTube cookies...")
    driver = setup_headless_browser()
    driver.get("https://accounts.google.com/ServiceLogin?service=youtube")

    try:
        # Find the email field, enter the username, and click next
        email_field = driver.find_element("name", "identifier")
        email_field.send_keys(username)
        driver.find_element("id", "identifierNext").click()
        time.sleep(2) # Wait for page transition

        # Find the password field, enter the password, and click next
        password_field = driver.find_element("name", "password")
        password_field.send_keys(password)
        driver.find_element("id", "passwordNext").click()
        time.sleep(5) # Wait for login to complete

        # Now that we are logged in, navigate to YouTube and extract cookies
        driver.get("https://www.youtube.com")
        cookies = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
        logger.info("Successfully retrieved YouTube cookies.")
        return cookies

    except Exception as e:
        logger.error(f"Failed to get cookies: {e}")
        return {}
    finally:
        driver.quit() # Always close the browser instance

# Startup function to get cookies once on startup
@app.on_event("startup")
async def startup_login():
    global YOUTUBE_COOKIES
    
    username = os.getenv("YOUTUBE_USERNAME")
    password = os.getenv("YOUTUBE_PASSWORD")
    
    if not username or not password:
        logger.error("YOUTUBE_USERNAME or YOUTUBE_PASSWORD environment variables are not set.")
        return
        
    YOUTUBE_COOKIES = get_youtube_cookies(username, password)

# API endpoint to download a video
@app.post("/api/download")
async def download_video(req: DownloadRequest):
    # Validate the URL
    if not YOUTUBE_REGEX.match(req.url):
        return {"error": "Invalid YouTube URL"}

    # Check if we have valid cookies
    if not YOUTUBE_COOKIES:
        return {"error": "Not authenticated. Please ensure the service has been configured with valid credentials."}

    filename = f"video_{int(time.time())}.mp4"
    output_path = str(DOWNLOAD_DIR / filename)

    # Convert the cookie dictionary to a string format for yt-dlp
    cookie_str = "; ".join([f"{name}={value}" for name, value in YOUTUBE_COOKIES.items()])

    # Pass the cookies directly to the yt-dlp command
    yt_dlp_cmd = [
        "yt-dlp",
        req.url,
        "--extractor-args", "youtube:player_client=android",
        "-o", output_path,
        "--add-header", f"Cookie:{cookie_str}", # Pass cookies in the header
        "--format", "ba",
        "--merge-output-format", "mp4",
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
