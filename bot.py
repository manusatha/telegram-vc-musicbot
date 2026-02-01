import os, asyncio
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped, InputStream

from config import *
from yt import search, download
from autoplay import recommend
from image import generate_thumbnail
from lyrics import get_lyrics
from radio import get_radio
from queue import add, pop, get, clear
from buttons import controls, search_buttons
from database import chats, history
from stats import add_play
from cleanup import cleanup

app = Client("musicbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
vc = PyTgCalls(app)

@app.on_message(filters.command("play") & filters.group)
async def play(_, m):
    q = " ".join(m.command[1:])
    if not q:
        return await m.reply("Give song name")
    res = search(q)
    await m.reply("Choose:", reply_markup=search_buttons(res))

@app.on_callback_query(filters.regex("^play_"))
async def play_cb(_, cb: CallbackQuery):
    url = cb.data.split("_", 1)[1]
    chat = cb.message.chat.id

    data = download(url)
    history.insert_one({"chat": chat, "title": data["title"]})
    add_play()
    cleanup()

    if vc.active_calls.get(chat):
        add(chat, data)
        return await cb.answer("Queued")

    chats.update_one({"_id": chat}, {"$set": {"volume": DEFAULT_VOLUME}}, upsert=True)
    await vc.join_group_call(chat, InputStream(AudioPiped(data["file"])))
    await vc.change_volume_call(chat, DEFAULT_VOLUME)

    thumb = generate_thumbnail(data["thumb"])
    await cb.message.delete()
    await app.send_photo(
        chat,
        photo=thumb,
        caption=f"🎵 {data['title']}",
        reply_markup=controls()
    )

@vc.on_stream_end()
async def next(_, u):
    chat = u.chat_id
    song = pop(chat)
    if song:
        await vc.change_stream(chat, InputStream(AudioPiped(song["file"])))
        return
    if AUTOPLAY:
        last = history.find_one({"chat": chat}, sort=[("_id", -1)])
        if last:
            url = recommend(last["title"])
            if url:
                data = download(url)
                await vc.change_stream(chat, InputStream(AudioPiped(data["file"])))
                return
    await vc.leave_group_call(chat)

@app.on_callback_query()
async def controls_cb(_, cb: CallbackQuery):
    chat = cb.message.chat.id
    if cb.data == "pause":
        await vc.pause_stream(chat)
    elif cb.data == "resume":
        await vc.resume_stream(chat)
    elif cb.data == "skip":
        song = pop(chat)
        if song:
            await vc.change_stream(chat, InputStream(AudioPiped(song["file"])))
        else:
            await vc.leave_group_call(chat)
    elif cb.data == "stop":
        clear(chat)
        await vc.leave_group_call(chat)
        await cb.message.edit("Stopped")
    elif cb.data == "lyrics":
        last = history.find_one({"chat": chat}, sort=[("_id", -1)])
        await cb.answer(get_lyrics(last["title"])[:4000], show_alert=True)
    elif cb.data == "radio":
        q = get_radio("lofi")
        r = search(q, 1)[0]
        data = download(r["webpage_url"])
        await vc.change_stream(chat, InputStream(AudioPiped(data["file"])))
    elif cb.data == "queue":
        await cb.answer("\n".join(x["title"] for x in get(chat)) or "Empty", show_alert=True)

vc.start()
app.run()
