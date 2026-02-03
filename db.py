import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_enabled_sources():
    res = supabase.table("sources").select("*").eq("is_active", True).execute()
    return res.data

def save_news(item):
    try:
        resp = supabase.table("news").upsert(item, on_conflict="hash").execute()
        if resp.status_code >= 400:
            print("❌ Ошибка при вставке новости в Supabase:", resp)
        else:
            return resp.data
    except Exception as e:
        print("❌ Исключение при сохранении новости:", e)