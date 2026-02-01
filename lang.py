LANG = {
    "en": {"now": "Now Playing", "empty": "Queue empty"},
    "si": {"now": "දැන් වාදනය වේ", "empty": "ගීත නැත"},
    "hi": {"now": "अभी चल रहा है", "empty": "कतार खाली है"},
}

def t(lang, key):
    return LANG.get(lang, LANG["en"]).get(key, key)
