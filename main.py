import os
import hashlib
import re
from datetime import datetime
import feedparser
from supabase import create_client, Client
from dedup import make_hash
from site import parse_site
from telegram import parse_telegram
from sites import sites as site_sources  # твои сайты
from telegram_sources import telegram_sources  # твои каналы

# --- Настройки Supabase ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- RSS Источники ---
RSS_SOURCES = {
    "war": [
        "https://ria.ru/export/rss2/defense.xml",
        "https://tass.ru/rss/v2.xml"
    ],
    "economy": [
        "https://www.vedomosti.ru/rss/news",
        "https://www.rbc.ru/rss/newsline.xml"
    ],
    "crypto": [],
    "world": [
        "https://ria.ru/export/rss2/world.xml"
    ],
    "tech": [
        "https://ria.ru/export/rss2/science.xml"
    ]
}

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

# --- Парсинг RSS ---
def parse_rss():
    all_news = []
    for category_slug, feeds in RSS_SOURCES.items():
        for url in feeds:
            print(f"Парсим RSS: {url}")
            try:
                feed = feedparser.parse(url)
            except Exception as e:
                print(f"❌ Ошибка при парсинге RSS {url}: {e}")
                continue

            for entry in feed.entries:
                title = (entry.get("title") or "").strip()
                link = (entry.get("link") or "").strip()
                summary = clean_html(entry.get("summary") or entry.get("description") or "")

                pub_date = entry.get("published_parsed") or entry.get("updated_parsed")
                if pub_date:
                    pub_date = datetime(*pub_date[:6])
                else:
                    pub_date = datetime.utcnow()

                news_hash = generate_hash(title, summary, link)
                short_summary = summary[:300] + ("..." if len(summary) > 300 else "")

                all_news.append({
                    "title": title or "Без заголовка",
                    "summary": short_summary,
                    "url": link or "Без ссылки",
                    "media_url": None,
                    "category_slug": category_slug,
                    "hash": news_hash,
                    "published_at": pub_date.isoformat(),
                    "is_nsfw": False
                })
    return all_news

# --- Сохранение в Supabase с проверкой дубликатов ---
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
    all_news = parse_rss()
    all_news += parse_site(source) for source in site_sources  # HTML сайты
    all_news += parse_telegram(source) for source in telegram_sources  # Telegram
    save_news(all_news)

if __name__ == "__main__":
    main()