queues = {}

def add(chat, song):
    queues.setdefault(chat, []).append(song)

def pop(chat):
    if queues.get(chat):
        return queues[chat].pop(0)

def get(chat):
    return queues.get(chat, [])

def clear(chat):
    queues.pop(chat, None)
