import feedparser
from dedup import make_hash

def parse_rss(source):
    feed = feedparser.parse(source["url"])
    items = []

    for entry in feed.entries:
        h = make_hash(entry.get("title",""), entry.get("link",""))

        image = None
        video = None
        if "media_content" in entry:
            for m in entry.media_content:
                if m.get("type","").startswith("image"):
                    image = m.get("url")
                elif m.get("type","").startswith("video"):
                    video = m.get("url")
        elif "enclosures" in entry and entry.enclosures:
            for e in entry.enclosures:
                if e.get("type","").startswith("image"):
                    image = e.get("url")
                elif e.get("type","").startswith("video"):
                    video = e.get("url")

        items.append({
            "source_id": source["id"],
            "category_id": source["category_id"],
            "title": entry.get("title",""),
            "summary": entry.get("summary",""),
            "url": entry.get("link",""),
            "image": image,
            "video": video,
            "published_at": entry.get("published", None),
            "hash": h,
            "is_nsfw": source.get("is_nsfw", False)
        })
    return items