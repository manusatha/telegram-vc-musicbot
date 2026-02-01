import requests

def get_lyrics(title):
    parts = title.split("-")
    artist = parts[0].strip()
    song = parts[-1].strip()

    r = requests.get(f"https://api.lyrics.ovh/v1/{artist}/{song}")
    if r.status_code == 200:
        return r.json().get("lyrics", "Lyrics not found.")
    return "Lyrics not found."
