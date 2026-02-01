from yt import search

def recommend(title):
    keywords = title.split()[:3]
    q = " ".join(keywords)
    res = search(q, 1)
    return res[0]["webpage_url"] if res else None
