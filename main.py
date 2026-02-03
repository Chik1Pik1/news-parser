import os
import requests
from bs4 import BeautifulSoup
import feedparser
from db import save_news

# Российские источники
SOURCES = [
    {
        "name": "РИА Новости",
        "type": "rss",
        "url": "https://ria.ru/export/rss2/index.xml",
        "category_slug": "world"
    },
    {
        "name": "ТАСС",
        "type": "rss",
        "url": "https://tass.ru/rss/v2.xml",
        "category_slug": "world"
    },
    {
        "name": "РБК",
        "type": "rss",
        "url": "https://rssexport.rbc.ru/rbcnews/news/",
        "category_slug": "economy"
    },
    {
        "name": "Ведомости",
        "type": "rss",
        "url": "https://www.vedomosti.ru/rss/news",
        "category_slug": "economy"
    },
    {
        "name": "Вести",
        "type": "rss",
        "url": "https://www.vesti.ru/vesti.rss",
        "category_slug": "war"
    },
    {
        "name": "CNews",
        "type": "rss",
        "url": "https://www.cnews.ru/news/top.rss",
        "category_slug": "tech"
    },
    {
        "name": "Lenta.ru",
        "type": "site",
        "url": "https://lenta.ru/",
        "category_slug": "world"
    },
]

def fetch_summary(entry):
    """Обрезаем текст до 300 символов и убираем HTML"""
    summary = entry.get("summary", "") or entry.get("description", "")
    summary_clean = BeautifulSoup(summary, "html.parser").get_text()
    summary_short = summary_clean[:300] + ("..." if len(summary_clean) > 300 else "")
    media_url = None
    if "media_content" in entry:
        media_url = entry.media_content[0]["url"]
    elif "media_thumbnail" in entry:
        media_url = entry.media_thumbnail[0]["url"]
    return summary_short, media_url

def parse_rss(source):
    items = []
    feed = feedparser.parse(source["url"])
    for entry in feed.entries[:10]:
        summary_short, media_url = fetch_summary(entry)
        items.append({
            "title": entry.get("title", "Без заголовка"),
            "summary": summary_short,
            "media_url": media_url,
            "category_slug": source["category_slug"]
        })
    return items

def parse_site(source):
    """Парсим главную страницу сайта, вытаскиваем заголовки и краткий текст"""
    items = []
    try:
        r = requests.get(source["url"], timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # Простейший пример для Lenta и Ведомости (адаптируй под сайт)
        articles = soup.find_all("a", class_="card-mini__link")[:10]
        for a in articles:
            title = a.get_text(strip=True)
            url = a.get("href")
            if not url.startswith("http"):
                url = source["url"].rstrip("/") + url
            # Получаем краткую суть новости с самой страницы
            try:
                r2 = requests.get(url, timeout=5)
                soup2 = BeautifulSoup(r2.text, "html.parser")
                p = soup2.find("p")
                summary = p.get_text(strip=True)[:300] + "..." if p else ""
                img_tag = soup2.find("img")
                media_url = img_tag.get("src") if img_tag else None
            except:
                summary = ""
                media_url = None

            items.append({
                "title": title,
                "summary": summary,
                "media_url": media_url,
                "category_slug": source["category_slug"]
            })

    except Exception as e:
        print(f"❌ Ошибка при парсинге сайта {source['name']}: {e}")
    return items

def run():
    total_saved = 0
    for source in SOURCES:
        print(f"\nПарсим: {source['name']} ({source['type']})")
        try:
            if source["type"] == "rss":
                items = parse_rss(source)
            elif source["type"] == "site":
                items = parse_site(source)
            else:
                print("Неизвестный тип источника")
                continue

            if not items:
                print("Ничего не найдено")
                continue

            for item in items:
                try:
                    save_news(item)
                    total_saved += 1
                    print("✅ Сохранили:", item["title"][:80])
                except Exception as e:
                    print("❌ Ошибка при сохранении:", e)

        except Exception as e:
            print("❌ Ошибка при парсинге источника:", e)

    print(f"\nПарсинг завершён. Сохранено новостей: {total_saved}")

if __name__ == "__main__":
    run()