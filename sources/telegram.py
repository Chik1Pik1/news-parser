from pyrogram import Client
from dedup import make_hash
import os

api_id = int(os.getenv("TG_API_ID", 0))
api_hash = os.getenv("TG_API_HASH", "")

app = Client("parser_session", api_id=api_id, api_hash=api_hash)

def parse_telegram(source, limit=10):
    items = []
    channel = source.get("channel")
    if not channel:
        return items
    with app:
        for msg in app.get_chat_history(channel, limit=limit):
            if not msg.text:
                continue
            h = make_hash(msg.text[:100], str(msg.id))
            items.append({
                "source_id": source["id"],
                "category_id": source["category_id"],
                "title": msg.text[:100],
                "summary": msg.text,
                "url": f"https://t.me/{channel}/{msg.id}",
                "published_at": msg.date.isoformat() if msg.date else None,
                "hash": h,
                "is_nsfw": False
            })
    return items
