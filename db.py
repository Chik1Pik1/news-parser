import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_enabled_sources():
    """
    Получаем все включённые источники новостей
    """
    res = supabase.table("sources").select("*").eq("is_active", True).execute()
    return res.data

def save_news(item):
    """
    Сохраняем новость в таблицу news.
    Использует upsert по hash, чтобы не дублировать.
    """
    try:
        resp = supabase.table("news").upsert(item, on_conflict="hash").execute()
        if resp.error:
            print("❌ Ошибка при вставке новости в Supabase:", resp.error)
        else:
            return resp.data
    except Exception as e:
        print("❌ Исключение при сохранении новости:", e)