import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_enabled_sources():
    res = supabase.table("sources").select("*").eq("enabled", True).execute()
    return res.data

def save_news(item):
    supabase.table("news").upsert(item, on_conflict="hash").execute()
