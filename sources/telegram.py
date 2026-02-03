from pyrogram import Client
from dedup import make_hash
import os

TG_API_ID = int(os.getenv("TG_API_ID", 0))
TG_API_HASH = os.getenv("TG_API_HASH")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "")

if TG_BOT_TOKEN:
    app = Client("bot_session", bot_token=TG_BOT_TOKEN)
    ENABLED = True
else:
    app = Client("parser_session", api_id=TG_API_ID, api_hash=TG_API_HASH)
    ENABLED = True  # обычный режим Pyrogram
            

def parse_telegram(source, limit=10):
    if not ENABLED:
        return []

    items = []
    channel = source.get("url")  # url = имя канала
    if not channel:
        return items

    with app:
        for msg in app.get_chat_history(channel, limit=limit):
            if not msg.text and not msg.photo and not msg.video:
                continue

            h = make_hash(msg.text[:100] if msg.text else str(msg.id), str(msg.id))
            image = msg.photo.file_id if msg.photo else None
            video = msg.video.file_id if msg.video else None

            items.append({
                "source_id": source["id"],
                "category_id": source["category_id"],
                "title": msg.text[:100] if msg.text else "",
                "summary": msg.text if msg.text else "",
                "url": f"https://t.me/{channel}/{msg.id}",
                "image": image,
                "video": video,
                "published_at": msg.date.isoformat() if msg.date else None,
                "hash": h,
                "is_nsfw": source.get("is_nsfw", False)
            })
    return items