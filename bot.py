import os, asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.player import MusicQueue
from utils.ffmpeg_utils import stream_audio
from config import BOT_TOKEN, API_ID, API_HASH

app = Client("musicbot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

music_queue = MusicQueue()
vc_process = None  # current FFmpeg process

# Start command
@app.on_message(filters.command("start"))
async def start(client, message):
    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🎵 Add Song", callback_data="add_song")]]
    )
    await message.reply_text(
        "Hello! I am your free Telegram VC Music Bot.\nUse buttons to control music.",
        reply_markup=buttons
    )

# Add a song to queue
@app.on_callback_query(filters.regex("add_song"))
async def add_song(client, query):
    await query.answer("Send me a YouTube link!")
    # Next message from user should contain the link
    # For simplicity, we can use a temporary message handler
    # (In production, track per-user state)

# Play command (manual)
@app.on_message(filters.command("play"))
async def play(client, message):
    global vc_process
    if music_queue.is_empty():
        await message.reply_text("Queue is empty!")
        return
    song = music_queue.pop()
    # Download via yt-dlp
    import yt_dlp
    ydl_opts = {"outtmpl": "downloads/%(title)s.%(ext)s", "format": "bestaudio"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(song, download=True)
        file_path = ydl.prepare_filename(info)
    # Stream to VC
    vc_process = stream_audio(file_path, chat_id=None)  # VC joining logic later
    await message.reply_text(f"Now playing: {info['title']}")

# Stop command
@app.on_message(filters.command("stop"))
async def stop(client, message):
    global vc_process
    if vc_process:
        vc_process.terminate()
        vc_process = None
        await message.reply_text("Stopped playback!")

# Run bot
app.run()
