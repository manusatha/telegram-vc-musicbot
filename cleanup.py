import os, time

def cleanup(path="downloads", age=3600):
    now = time.time()
    for f in os.listdir(path):
        fp = os.path.join(path, f)
        if os.path.isfile(fp) and now - os.path.getmtime(fp) > age:
            os.remove(fp)
