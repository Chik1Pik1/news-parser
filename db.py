import os
from supabase import create_client

SUPABASE_URL = os.getenv("https://rltppxkgyasyfkftintn.supabase.co")
SUPABASE_KEY = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJsdHBweGtneWFzeWZrZnRpbnRuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDA1MzQ0MCwiZXhwIjoyMDg1NjI5NDQwfQ.ezQikofIISwy-Z3oMc5NrMnWF6DB3qe8srDApH9OpF8")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_enabled_sources():
    res = supabase.table("sources").select("*").eq("enabled", True).execute()
    return res.data

def save_news(item):
    supabase.table("news").upsert(item, on_conflict="hash").execute()
