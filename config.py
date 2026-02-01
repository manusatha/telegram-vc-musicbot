import os

class Config:
    API_ID = int(os.getenv("API_ID", "12345"))
    API_HASH = os.getenv("API_HASH", "your_api_hash")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")
    # This is the Pyrogram String Session for the User Account (Assistant)
    SESSION = os.getenv("SESSION", "your_pyrogram_string_session")
