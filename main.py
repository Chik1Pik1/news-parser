from db import get_enabled_sources, save_news
from sources.rss import parse_rss
from sources.site import parse_site
import requests
from bs4 import BeautifulSoup

try:
    from sources.telegram import parse_telegram
    TELEGRAM_ENABLED = True
except ImportError:
    TELEGRAM_ENABLED = False

def fetch_full_text(url):
    """
    Получаем полный текст новости с сайта по ссылке
    """
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        # Ищем основной контейнер статьи
        article = soup.find("article")
        if not article:
            divs = soup.find_all("div")
            if divs:
                article = max(divs, key=lambda d: len(d.get_text()))
            else:
                return None

        # Удаляем лишние теги
        for tag in article(["script", "style", "aside", "nav"]):
            tag.decompose()

        text = article.get_text(separator="\n", strip=True)
        return text
    except Exception as e:
        print("❌ Не удалось получить полный текст:", url, e)
        return None

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
                try:
                    # Для RSS и сайтов получаем полный текст
                    if source["type"] in ["rss", "site"] and item.get("url"):
                        full_text = fetch_full_text(item["url"])
                        if full_text:
                            item["content"] = full_text
                        else:
                            item["content"] = item.get("summary", "")
                    # Для Telegram используем текст поста
                    elif source["type"] == "telegram":
                        item["content"] = item.get("summary", "")

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