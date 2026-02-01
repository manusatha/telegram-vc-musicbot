import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from utils.player import MusicQueue
from utils.ffmpeg_utils import stream_audio
from config import BOT_TOKEN, API_ID, API_HASH, DOWNLOAD_PATH, MONGO_URI
from pymongo import MongoClient
import yt_dlp

# Ensure downloads folder exists
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

app = Client("musicbot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)
music_queue = MusicQueue()
vc_process = None

# MongoDB setup
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["musicbot"]
queue_collection = db["queue"]

# --- Helper functions ---
async def download_song(url: str):
    ydl_opts = {"outtmpl": f"{DOWNLOAD_PATH}/%(title)s.%(ext)s", "format": "bestaudio"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)
        return file_path, info.get("title", "Unknown")

async def play_next(message: Message):
    global vc_process
    if music_queue.is_empty():
        await message.reply_text("Queue finished!")
        return
    song = music_queue.pop()
    file_path, title = await download_song(song)
    vc_process = stream_audio(file_path)
    await message.reply_text(f"Now playing: {title}")
    # Wait until song finishes
    await asyncio.sleep(1)  # small delay to start streaming
    while vc_process.poll() is None:
        await asyncio.sleep(1)
    # Play next
    await play_next(message)

# --- Bot commands ---
@app.on_message(filters.command("start"))
async def start(client, message):
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🎵 Add Song", callback_data="add_song")],
            [InlineKeyboardButton("⏯ Stop", callback_data="stop")]
        ]
    )
    await message.reply_text(
        "Hello! I am your free Telegram VC Music Bot.\nUse buttons below to control music.",
        reply_markup=buttons
    )

@app.on_callback_query(filters.regex("add_song"))
async def add_song(client, query):
    await query.answer("Send me a YouTube link now!")

    # Wait for next message from the same user
    @app.on_message(filters.private & filters.user(query.from_user.id))
    async def get_link(_, message):
        url = message.text.strip()
        music_queue.add(url)
        queue_collection.insert_one({"song": url})
        await message.reply_text(f"Added to queue: {url}")
        # If nothing is playing, start
        if vc_process is None or vc_process.poll() is not None:
            await play_next(message)
        app.remove_handler(get_link)

@app.on_callback_query(filters.regex("stop"))
async def stop_music(client, query):
    global vc_process
    if vc_process:
        vc_process.terminate()
        vc_process = None
        music_queue.clear()
        await query.message.reply_text("Stopped playback and cleared queue!")
    await query.answer()

# Run the bot
app.run()
