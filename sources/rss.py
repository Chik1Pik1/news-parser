import feedparser
from dedup import make_hash

def parse_rss(source):
    feed = feedparser.parse(source["url"])
    items = []
    for entry in feed.entries:
        h = make_hash(entry.get("title",""), entry.get("link",""))
        items.append({
            "source_id": source["id"],
            "category_id": source["category_id"],
            "title": entry.get("title",""),
            "summary": entry.get("summary",""),
            "url": entry.get("link",""),
            "published_at": entry.get("published", None),
            "hash": h,
            "is_nsfw": False
        })
    return items
