from db import get_enabled_sources, save_news
from rss import parse_rss
from site import parse_site

try:
    from telegram import parse_telegram, ENABLED as TG_ENABLED
except ImportError:
    TG_ENABLED = False

def run():
    sources = get_enabled_sources()
    if not sources:
        print("Нет включённых источников")
        return

    for source in sources:
        try:
            print(f"\nПарсим: {source.get('name')} ({source.get('type')})")
            items = []

            if source["type"] == "rss":
                items = parse_rss(source)
            elif source["type"] == "site":
                items = parse_site(source)
            elif source["type"] == "telegram":
                if TG_ENABLED:
                    items = parse_telegram(source)
                else:
                    print("Telegram отключён")
                    continue
            else:
                print("Неизвестный тип:", source["type"])
                continue

            if not items:
                print("Ничего не найдено")
                continue

            for item in items:
                try:
                    save_news(item)
                    print("Сохранили:", item["title"][:80])
                except Exception as e:
                    print("Ошибка сохранения:", e)

        except Exception as e:
            print("Ошибка парсинга:", source.get("name"), e)

if __name__ == "__main__":
    try:
        run()
        print("\nПарсинг завершён")
    except Exception as e:
        print("Ошибка в основном цикле:", e)