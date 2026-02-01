from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def controls():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏸", "pause"),
            InlineKeyboardButton("▶️", "resume"),
            InlineKeyboardButton("⏭", "skip"),
            InlineKeyboardButton("⏹", "stop")
        ],
        [
            InlineKeyboardButton("📄 Lyrics", "lyrics"),
            InlineKeyboardButton("📻 Radio", "radio")
        ],
        [
            InlineKeyboardButton("🔊 +", "volup"),
            InlineKeyboardButton("🔉 -", "voldown"),
            InlineKeyboardButton("📜 Queue", "queue")
        ]
    ])

def search_buttons(results):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(r["title"][:40], f"play_{r['webpage_url']}")]
        for r in results
    ])
