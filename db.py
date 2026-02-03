# db.py
from supabase import create_client
from datetime import datetime

# 🔹 Подставляем твой Service Role Key для вставки
SUPABASE_URL = "https://rltppxkgyasyfkftintn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJsdHBweGtneWFzeWZrZnRpbnRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwNTM0NDAsImV4cCI6MjA4NTYyOTQ0MH0.98RP1Ci9UFkjhKbi1woyW5dbRbXJ8qNdopM1aJMSdf4"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_enabled_sources():
    res = supabase.table("sources").select("*").eq("is_active", True).execute()
    if res.error:
        print("Ошибка при получении источников:", res.error)
        return []
    return res.data

def save_news(item):
    # 🔹 Преобразуем published_at в ISO, если есть
    if item.get("published_at"):
        try:
            item["published_at"] = datetime.fromisoformat(item["published_at"])
        except Exception:
            item["published_at"] = None

    res = supabase.table("news").upsert(item, on_conflict="hash").execute()
    if res.error:
        print("Ошибка при сохранении новости:", res.error)
    else:
        print(f"Сохранили новость: {item.get('title')[:80]}")