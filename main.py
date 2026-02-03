import feedparser
import html
from datetime import datetime
from supabase import create_client, Client
import hashlib

# --- Supabase ---
SUPABASE_URL = "https://rltppxkgyasyfkftintn.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJsdHBweGtneWFzeWZrZnRpbnRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwNTM0NDAsImV4cCI6MjA4NTYyOTQ0MH0.98RP1Ci9UFkjhKbi1woyW5dbRbXJ8qNdopM1aJMSdf4"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# --- Категории ---
CATEGORIES = {
    "war": "Военные новости",
    "economy": "Экономика",
    "crypto": "Криптовалюта",
    "world": "Мир",
    "tech": "Технологии"
}

# --- RSS источники ---
RSS_SOURCES = [
    {"name": "РИА Новости", "url": "https://ria.ru/export/rss2/all.xml", "category": "world"},
    {"name": "ТАСС", "url": "https://tass.ru/rss/v2.xml", "category": "world"},
    {"name": "РБК", "url": "https://www.rbc.ru/rss/newsline.xml", "category": "economy"},
    {"name": "Ведомости", "url": "https://www.vedomosti.ru/rss/news", "category": "economy"},
    {"name": "Вести", "url": "https://www.vesti.ru/vesti.rss", "category": "war"},
    {"name": "CNews", "url": "https://www.cnews.ru/news/rss", "category": "tech"},
    {"name": "Lenta.ru", "url": "https://lenta.ru/rss/news", "category": "crypto"},
]

def summarize_text(text, max_len=300):
    """Обрезаем текст до короткой сути и убираем HTML теги"""
    text = html.unescape(text)
    text = text.replace("\n", " ").replace("\r", " ")
    if len(text) > max_len:
        return text[:max_len].rstrip() + "..."
    return text

def generate_hash(title, url):
    """Уникальный хэш для новости"""
    return hashlib.md5((title + (url or "")).encode("utf-8")).hexdigest()

def save_news_to_db(news_item):
    """Сохраняем новость в Supabase"""
    try:
        # конвертируем datetime в строку
        if isinstance(news_item.get("created_at"), datetime):
            news_item["created_at"] = news_item["created_at"].isoformat()
        response = supabase.table("news").insert(news_item).execute()
        if response.error:
            print(f"❌ Ошибка при сохранении: {response.error}")
        else:
            print(f"✅ Сохранено: {news_item['title'][:50]}...")
    except Exception as e:
        print(f"❌ Ошибка при сохранении: {e}")

def parse_rss(source):
    print(f"Парсим RSS: {source['url']}")
    feed = feedparser.parse(source["url"])
    saved_count = 0
    for entry in feed.entries:
        title = entry.get("title", "Без заголовка")
        description = summarize_text(entry.get("description", "") or entry.get("summary", ""))
        url = entry.get("link")
        created_at = entry.get("published_parsed")
        if created_at:
            created_at = datetime(*created_at[:6])
        else:
            created_at = datetime.utcnow()
        news_item = {
            "title": title,
            "summary": description,
            "url": url or "https://example.com",  # чтобы не было null
            "category_slug": source["category"],
            "hash": generate_hash(title, url),
            "created_at": created_at,
        }
        save_news_to_db(news_item)
        saved_count += 1
    print(f"Парсинг завершён. Сохранено новостей: {saved_count}")

def main():
    for source in RSS_SOURCES:
        parse_rss(source)

if __name__ == "__main__":
    main()