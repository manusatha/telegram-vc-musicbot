import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
MONGO_URI = os.environ.get("MONGO_URI")
OWNER_ID = int(os.environ.get("OWNER_ID", 0))  # optional

# FFmpeg path for Heroku
FFMPEG_BIN = "ffmpeg"  # Heroku already has ffmpeg installed
