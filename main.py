import os
import requests
from bs4 import BeautifulSoup
from db import get_enabled_sources, save_news
from sources.rss import parse_rss
from sources.site import parse_site

try:
    from sources.telegram import parse_telegram
    TELEGRAM_ENABLED = True
except ImportError:
    TELEGRAM_ENABLED = False

def fetch_full_text(url):
    """ Получаем полный текст статьи с сайта """
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        paragraphs = soup.find_all("p")
        full_text = "\n\n".join(p.get_text() for p in paragraphs if p.get_text().strip())
        return full_text
    except Exception as e:
        print("❌ Ошибка при fetch_full_text:", e)
        return ""

def run():
    sources = get_enabled_sources()
    if not sources:
        print("Нет включённых источников для парсинга")
        return

    total_saved = 0

    for source in sources:
        try:
            print(f"\nПарсим: {source.get('name')} ({source.get('type')})")
            items = []

            if source["type"] == "rss":
                items = parse_rss(source)
            elif source["type"] == "site":
                items = parse_site(source)
            elif source["type"] == "telegram":
                if TELEGRAM_ENABLED:
                    items = parse_telegram(source)
                else:
                    print("Telegram-парсер отключён, пропускаем")
                    continue
            else:
                print("Неизвестный тип источника:", source["type"])
                continue

            if not items:
                print("Ничего не найдено для источника:", source.get("name"))
                continue

            for item in items:
                # Получаем полный текст статьи
                if "url" in item and item["url"]:
                    full_text = fetch_full_text(item["url"])
                    if full_text:
                        item["summary"] = full_text  # сохраняем полный текст в summary

                try:
                    save_news(item)
                    total_saved += 1
                    print("✅ Сохранили:", item["title"][:80])
                except Exception as e:
                    print("❌ Исключение при сохранении новости:", e)

        except Exception as e:
            print("❌ Ошибка при парсинге источника:", source.get("name"), e)

    print(f"\nПарсинг завершён. Сохранено новостей: {total_saved}")

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print("❌ Ошибка в основном цикле парсера:", e)