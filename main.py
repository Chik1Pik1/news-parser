import feedparser
from datetime import datetime
import hashlib
import re
from supabase import create_client, Client

# --- Настройки Supabase ---
SUPABASE_URL = "https://rltppxkgyasyfkftintn.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJsdHBweGtneWFzeWZrZnRpbnRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwNTM0NDAsImV4cCI6MjA4NTYyOTQ0MH0.98RP1Ci9UFkjhKbi1woyW5dbRbXJ8qNdopM1aJMSdf4"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# --- Источники новостей по категориям ---
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
        # Можно добавить русские сайты про крипту, например forklog, cointelegraph.ru
    ],
    "world": [
        "https://ria.ru/export/rss2/world.xml"
    ],
    "tech": [
        "https://ria.ru/export/rss2/science.xml"
    ]
}

# --- Функция для очистки HTML ---
def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()

# --- Функция для генерации хэша новости ---
def generate_hash(title, summary, url):
    text = (title + summary + (url or "")).encode("utf-8")
    return hashlib.sha256(text).hexdigest()

# --- Главная функция парсинга ---
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
                summary = clean_html(entry.get("summary", "") or entry.get("description", ""))
                
                pub_date = entry.get("published_parsed") or entry.get("updated_parsed")
                if pub_date:
                    pub_date = datetime(*pub_date[:6])
                else:
                    pub_date = datetime.utcnow()

                news_hash = generate_hash(title, summary, link)

                # --- Проверяем, есть ли уже такой хэш ---
                existing = supabase.table("news").select("id").eq("hash", news_hash).execute()
                if existing.data and len(existing.data) > 0:
                    continue  # уже есть — пропускаем

                # Ограничиваем текст до ~300 символов для "анонса"
                short_summary = summary
                if len(summary) > 300:
                    short_summary = summary[:300] + "..."

                news_item = {
                    "title": title or "Без заголовка",
                    "url": link or "Без ссылки",
                    "summary": short_summary,
                    "category_slug": category_slug,
                    "hash": news_hash,
                    "published_at": pub_date.isoformat()
                }

                news_to_save.append(news_item)

            if news_to_save:
                response = supabase.table("news").insert(news_to_save).execute()
                if hasattr(response, "error") and response.error:
                    print("❌ Ошибка при сохранении:", response.error)
                else:
                    total_saved += len(news_to_save)
                    print(f"✅ Сохранено новостей: {len(news_to_save)}")

    print("Парсинг завершён. Всего сохранено новостей:", total_saved)

if __name__ == "__main__":
    fetch_and_save_news()