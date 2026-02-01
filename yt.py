import yt_dlp, os

DOWNLOADS = "downloads"
os.makedirs(DOWNLOADS, exist_ok=True)

def search(query, limit=5):
    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        data = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
        return data["entries"]

def download(url):
    ydl_opts = {
        "format": "bestaudio",
        "outtmpl": f"{DOWNLOADS}/%(id)s.%(ext)s",
        "quiet": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return {
            "file": ydl.prepare_filename(info),
            "title": info["title"],
            "thumb": info["thumbnail"]
      }
