import os
import hashlib
import re
from datetime import datetime
import feedparser
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
from dedup import make_hash  # для HTML парсера

# --- Настройки Supabase ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Источники RSS по категориям ---
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

                news_item = {
                    "title": title or "Без заголовка",
                    "summary": short_summary,
                    "url": link or "Без ссылки",
                    "media_url": None,  # можно добавить, если есть media_content
                    "category_slug": category_slug,
                    "hash": news_hash,
                    "published_at": pub_date.isoformat(),
                    "is_nsfw": False
                }

                all_news.append(news_item)
    return all_news

# --- Парсинг сайтов (HTML) ---
def parse_sites(sources):
    all_news = []
    for source in sources:
        try:
            resp = requests.get(source["url"], timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")
            selector = source.get("selector")
            if not selector:
                continue

            for a in soup.select(selector):
                title = a.get_text(strip=True)
                link = a.get("href")
                if not title or not link:
                    continue
                if not link.startswith("http"):
                    link = source["url"].rstrip("/") + "/" + link.lstrip("/")

                news_hash = make_hash(title, link)
                img = a.find("img")
                media_url = img["src"] if img else None

                news_item = {
                    "title": title,
                    "summary": "",
                    "url": link,
                    "media_url": media_url,
                    "category_slug": source["category_slug"],
                    "hash": news_hash,
                    "published_at": None,
                    "is_nsfw": False
                }
                all_news.append(news_item)
        except Exception as e:
            print(f"❌ Ошибка при парсинге сайта {source['name']}: {e}")
    return all_news

# --- Сохранение новостей в Supabase с проверкой дубликатов ---
def save_news(news_list):
    saved = 0
    for item in news_list:
        try:
            # Проверяем, есть ли такой хэш
            existing = supabase.table("news").select("id").eq("hash", item["hash"]).execute()
            if existing.data and len(existing.data) > 0:
                continue  # Уже есть — пропускаем

            # Вставляем только новые
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
    # Если есть сайты, можно добавить: all_news += parse_sites(site_sources)
    save_news(all_news)

if __name__ == "__main__":
    main()