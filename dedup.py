import hashlib

def make_hash(title, url):
    raw = (title + url).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()
