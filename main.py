import os
import hashlib
import re
from datetime import datetime
from supabase import create_client, Client
from dedup import make_hash

# --- Импорты из папки sources ---
from sources.parser_site import parse_site
from sources.telegram import parse_telegram
from sources.rss import parse_rss

from sites import sites as site_sources              # твои сайты
from telegram_sources import telegram_sources       # твои Telegram-каналы

# --- Настройки Supabase ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Очистка HTML ---
def clean_html(raw_html):
    if not raw_html:
        return ""
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html).strip()

# --- Генерация хэша ---
def generate_hash(title, summary, url):
    text = (title + summary + (url or "")).encode("utf-8")
    return hashlib.sha256(text).hexdigest()

# --- Сохранение новостей с проверкой дубликатов ---
def save_news(news_list):
    saved = 0
    for item in news_list:
        try:
            existing = supabase.table("news").select("id").eq("hash", item["hash"]).execute()
            if existing.data and len(existing.data) > 0:
                continue
            response = supabase.table("news").insert(item).execute()
            if hasattr(response, "error") and response.error:
                continue
            saved += 1
        except Exception as e:
            print(f"❌ Ошибка при вставке новости: {e}")
    print(f"✅ Всего сохранено новостей: {saved}")

# --- Главная функция ---
def main():
    all_news = []

    # --- RSS ---
    rss_news = parse_rss()
    all_news += rss_news

    # --- HTML сайты ---
    for source in site_sources:
        site_news = parse_site(source)
        all_news += site_news

    # --- Telegram ---
    for source in telegram_sources:
        tg_news = parse_telegram(source)
        all_news += tg_news

    # --- Сохраняем всё в Supabase ---
    save_news(all_news)

if __name__ == "__main__":
    main()