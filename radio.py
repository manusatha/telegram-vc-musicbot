RADIOS = {
    "lofi": "lofi hip hop beats",
    "edm": "edm festival mix",
    "anime": "anime opening songs",
    "classical": "classical orchestra"
}

def get_radio(mode):
    return RADIOS.get(mode, "lofi hip hop")
