from pyrogram import Client
from dedup import make_hash
import os

bot_token = os.getenv("TG_BOT_TOKEN")
api_id = int(os.getenv("TG_API_ID", 0))
api_hash = os.getenv("TG_API_HASH", "")

app = Client("parser_bot_session", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

def parse_telegram(source, limit=10):
    items = []
    channel = source.get("channel")
    if not channel:
        return items

    try:
        with app:
            for msg in app.get_chat_history(channel, limit=limit):
                if not msg.text and not msg.photo and not msg.video:
                    continue

                content = msg.text or ""
                h = make_hash(content[:100], str(msg.id))

                media_url = None
                if msg.photo:
                    media_url = msg.photo.file_id
                elif msg.video:
                    media_url = msg.video.file_id

                items.append({
                    "source_id": source["id"],
                    "category_id": source["category_id"],
                    "title": content[:100],
                    "summary": content,
                    "url": f"https://t.me/{channel}/{msg.id}",
                    "published_at": msg.date.isoformat() if msg.date else None,
                    "hash": h,
                    "is_nsfw": False,
                    "media_url": media_url
                })
        print(f"Найдено {len(items)} сообщений в Telegram: {source['name']}")
    except Exception as e:
        print(f"❌ Ошибка при парсинге Telegram {source['name']}: {e}")

    return items