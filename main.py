import feedparser
import requests
from bs4 import BeautifulSoup
import hashlib
from datetime import datetime
from supabase import create_client, Client

# --- Supabase ---
SUPABASE_URL = "https://rltppxkgyasyfkftintn.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJsdHBweGtneWFzeWZrZnRpbnRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwNTM0NDAsImV4cCI6MjA4NTYyOTQ0MH0.98RP1Ci9UFkjhKbi1woyW5dbRbXJ8qNdopM1aJMSdf4"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# --- RSS / сайты ---
NEWS_SOURCES = {
    "РИА Новости": "https://ria.ru/export/rss2/all.xml",
    "ТАСС": "https://tass.ru/rss/v2.xml",
    "РБК": "https://www.rbc.ru/rss/newsline.xml",
    "Ведомости": "https://www.vedomosti.ru/rss/news",
    "Вести": "https://www.vesti.ru/vesti.rss",
}

# --- Категории ---
CATEGORIES = {
    "crypto": "Криптовалюта",
    "economy": "Экономика",
    "war": "Военные новости",
    "world": "Мир",
    "tech": "Технологии",
}

# --- Функции ---
def clean_text(html_text, limit=300):
    """Удаляет HTML-теги и делает короткий превью"""
    soup = BeautifulSoup(html_text or "", "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    # Обрезаем до limit символов
    if len(text) > limit:
        text = text[:limit].rstrip() + "..."
    return text

def generate_hash(title, text, url):
    """Создаем md5 hash по title + text + url"""
    s = (title + text + (url or "")).encode("utf-8")
    return hashlib.md5(s).hexdigest()

def save_news_to_db(news_item):
    """Сохраняем новость в Supabase"""
    try:
        response = supabase.table("news").insert(news_item).execute()
        if response.error:
            print(f"❌ Ошибка при сохранении: {response.error}")
        else:
            print(f"✅ Сохранено: {news_item['title'][:50]}...")
    except Exception as e:
        print(f"❌ Ошибка при сохранении: {e}")

# --- Парсер RSS ---
def parse_rss(url, category_slug):
    print(f"Парсим RSS: {url}")
    feed = feedparser.parse(url)
    count = 0
    for entry in feed.entries[:10]:  # берем максимум 10 новостей
        title = entry.get("title", "Без заголовка")
        url = entry.get("link") or ""
        summary = entry.get("summary") or entry.get("description") or ""
        text = clean_text(summary, limit=300)
        hash_value = generate_hash(title, text, url)
        news_data = {
            "title": title,
            "text": text,
            "url": url,
            "category_slug": category_slug,
            "hash": hash_value,
            "created_at": datetime.utcnow(),
        }
        save_news_to_db(news_data)
        count += 1
    print(f"Парсинг завершён. Сохранено новостей: {count}")

# --- Основной цикл ---
def main():
    for source_name, rss_url in NEWS_SOURCES.items():
        # Для простоты все новости ставим в категорию "world" (можно расширить логику по словарю)
        parse_rss(rss_url, "world")

if __name__ == "__main__":
    main()