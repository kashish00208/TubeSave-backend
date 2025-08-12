# YouTube Downloader API

A FastAPI application that downloads YouTube videos using `yt-dlp` and manages authentication automatically with a headless browser.

---

##  Features

* **API-driven:** Download videos via a simple REST API endpoint.
* **Automatic Authentication:** Uses a headless browser to get fresh YouTube session cookies, so you don't have to manually update them.
* **Containerized & Cloud-Ready:** Designed for easy deployment on platforms like Render.

---

## Getting Started

### Prerequisites

You need **Python 3.10+** and **pip** installed on your system.

### Installation

Clone the repository and install the required packages.

```bash
git clone <your-repo-url>
cd <your-repo-name>/src
pip install -r requirements.txt