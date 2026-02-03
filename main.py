import feedparser
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
from datetime import datetime
import hashlib

# --- Supabase ---
SUPABASE_URL = "https://rltppxkgyasyfkftintn.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJsdHBweGtneWFzeWZrZnRpbnRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwNTM0NDAsImV4cCI6MjA4NTYyOTQ0MH0.98RP1Ci9UFkjhKbi1woyW5dbRbXJ8qNdopM1aJMSdf4"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# --- Настройки RSS ---
RSS_SOURCES = {
    "war": [
        "https://ria.ru/export/rss2/defense.xml",
        "https://tass.ru/rss/v2.xml"
    ],
    "economy": [
        "https://www.vedomosti.ru/rss/news",
        "https://www.rbc.ru/rss/newsline.xml"
    ],
    "crypto": [
        "https://www.rbc.ru/rss/crypto.xml"
    ],
    "world": [
        "https://www.vesti.ru/vesti.rss"
    ],
    "tech": [
        "https://www.cnews.ru/rss/news/"
    ]
}

MAX_TEXT_LENGTH = 300  # длина новости для показа

# --- Функции ---
def clean_html(raw_html):
    """Убираем теги HTML и лишние пробелы"""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    if len(text) > MAX_TEXT_LENGTH:
        text = text[:MAX_TEXT_LENGTH] + "..."
    return text

def generate_hash(title, summary, url):
    """Генерируем хэш для уникальности новости"""
    raw = (title or "") + (summary or "") + (url or "")
    return hashlib.md5(raw.encode("utf-8")).hexdigest()

def fetch_and_save_news():
    total_saved = 0
    for category_slug, feeds in RSS_SOURCES.items():
        for url in feeds:
            print(f"Парсим RSS: {url}")
            try:
                feed = feedparser.parse(url)
            except Exception as e:
                print("❌ Ошибка при парсинге:", e)
                continue

            news_to_save = []
            for entry in feed.entries:
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                summary = clean_html(entry.get("summary", ""))
                pub_date = entry.get("published_parsed") or entry.get("updated_parsed")
                if pub_date:
                    pub_date = datetime(*pub_date[:6])
                else:
                    pub_date = datetime.utcnow()

                news_item = {
                    "title": title,
                    "url": link,
                    "summary": summary,
                    "category_slug": category_slug,
                    "hash": generate_hash(title, summary, link),
                    "published_at": pub_date.isoformat()
                }

                news_to_save.append(news_item)

            if news_to_save:
                response = supabase.table("news").insert(news_to_save).execute()
                if response.status_code >= 400:
                    print("❌ Ошибка при сохранении:", response.data)
                else:
                    total_saved += len(news_to_save)
                    print(f"✅ Сохранено новостей: {len(news_to_save)}")
    print("Парсинг завершён. Всего сохранено новостей:", total_saved)


if __name__ == "__main__":
    fetch_and_save_news()