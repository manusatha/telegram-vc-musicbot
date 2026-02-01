import os
import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from yt_dlp import YoutubeDL
from config import Config

# Initialize Bot and User (Assistant) Clients
bot = Client(
    "MusicBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)

user = Client(
    "MusicAssistant",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    session_string=Config.SESSION
)

# Initialize PyTgCalls
call_py = PyTgCalls(user)

@bot.on_message(filters.command("play") & filters.group)
async def play(client, message):
    chat_id = message.chat.id
    
    if len(message.command) < 2:
        await message.reply_text("❌ **Usage:** /play <Song Name or URL>")
        return

    query = " ".join(message.command[1:])
    m = await message.reply_text("🔎 **Searching...**")

    # Search YouTube using yt-dlp
    try:
        ydl_opts = {"format": "bestaudio", "noplaylist": True, "quiet": True}
        with YoutubeDL(ydl_opts) as ydl:
            if "http" in query:
                info = ydl.extract_info(query, download=False)
            else:
                info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
                
            url = info['url']
            title = info['title']
    except Exception as e:
        await m.edit(f"❌ **Error:** Unable to find song.\n`{e}`")
        return

    # Stream the Audio
    try:
        await call_py.play(
            chat_id,
            MediaStream(
                url,
            )
        )
        await m.edit(f"🎵 **Playing:** [{title}]({info['webpage_url']})")
    except Exception as e:
        await m.edit(f"❌ **Error Joining Voice Chat:**\n`{e}`\n\n*Make sure the Assistant Account is a member of this group!*")

@bot.on_message(filters.command("stop") & filters.group)
async def stop(client, message):
    try:
        await call_py.leave_call(message.chat.id)
        await message.reply_text("⏹ **Stopped Streaming.**")
    except Exception:
        await message.reply_text("❌ **Not streaming anything.**")

async def start_bot():
    print("starting bot...")
    await bot.start()
    await user.start()
    await call_py.start()
    print("Bot Started!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
