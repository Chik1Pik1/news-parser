import feedparser
from dedup import make_hash

def parse_rss(source):
    feed = feedparser.parse(source["url"])
    items = []
    for entry in feed.entries:
        h = make_hash(entry.get("title",""), entry.get("link",""))

        media_url = None
        if "media_content" in entry:
            media_url = entry.media_content[0].get("url")

        items.append({
            "source_id": source["id"],
            "category_id": source["category_id"],
            "title": entry.get("title",""),
            "summary": entry.get("summary",""),
            "url": entry.get("link",""),
            "published_at": entry.get("published", None),
            "hash": h,
            "is_nsfw": False,
            "media_url": media_url
        })
    print(f"Найдено {len(items)} новостей в RSS: {source['name']}")
    return items