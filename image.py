from PIL import Image
import requests, io

def generate_thumbnail(url):
    base = Image.open(io.BytesIO(requests.get(url).content)).convert("RGBA")
    logo = Image.open("logo.png").convert("RGBA")

    logo = logo.resize((base.width // 5, base.height // 5))
    base.paste(
        logo,
        (base.width - logo.width - 20, base.height - logo.height - 20),
        logo
    )

    out = "thumb.png"
    base.save(out)
    return out
