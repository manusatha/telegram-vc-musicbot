import os
import asyncio
import subprocess
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pymongo import MongoClient
import yt_dlp
from collections import deque

# --- Config ---
from config import BOT_TOKEN, API_ID, API_HASH, DOWNLOAD_PATH, MONGO_URI, FFMPEG_BIN

os.makedirs(DOWNLOAD_PATH, exist_ok=True)

app = Client("musicbot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

# --- Queue system ---
music_queue = deque()
vc_process = None

# --- MongoDB ---
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

def stream_audio(file_path):
    cmd = [FFMPEG_BIN, "-re", "-i", file_path, "-f", "s16le", "-ar", "48000", "-ac", "2", "pipe:1"]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE)

async def play_next(message: Message):
    global vc_process
    if not music_queue:
        await message.reply_text("Queue finished!")
        return
    song = music_queue.popleft()
    file_path, title = await download_song(song)
    vc_process = stream_audio(file_path)
    await message.reply_text(f"Now playing: {title}")
    await asyncio.sleep(1)
    while vc_process.poll() is None:
        await asyncio.sleep(1)
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

    @app.on_message(filters.private & filters.user(query.from_user.id))
    async def get_link(_, message):
        url = message.text.strip()
        music_queue.append(url)
        queue_collection.insert_one({"song": url})
        await message.reply_text(f"Added to queue: {url}")
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

# --- Run bot ---
app.run()
