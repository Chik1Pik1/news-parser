import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_enabled_sources():
    """Возвращает все включённые источники новостей"""
    try:
        res = supabase.table("sources").select("*").eq("is_active", True).execute()
        return res.data or []
    except Exception as e:
        print("❌ Ошибка при получении источников:", e)
        return []

def save_news(item):
    """Сохраняет новость в таблицу news с upsert по hash"""
    try:
        resp = supabase.table("news").upsert(item, on_conflict="hash").execute()
        if not resp.data:
            print("❌ Не удалось сохранить новость, resp.data пустой:", item.get("title", "")[:80])
        else:
            return resp.data
    except Exception as e:
        print("❌ Исключение при сохранении новости:", e)