import time
START = time.time()
plays = 0

def uptime():
    s = int(time.time() - START)
    return f"{s//3600}h {(s%3600)//60}m"

def add_play():
    global plays
    plays += 1
