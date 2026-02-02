from db import get_enabled_sources, save_news
from sources.rss import parse_rss
from sources.site import parse_site

# Попробуем импортировать Telegram парсер, если есть настройки
try:
    from sources.telegram import parse_telegram
    TELEGRAM_ENABLED = True
except ImportError:
    TELEGRAM_ENABLED = False

def run():
    sources = get_enabled_sources()
    if not sources:
        print("Нет включённых источников для парсинга")
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

            # Сохраняем все новости
            for item in items:
                try:
                    save_news(item)
                    print("Сохранили:", item["title"][:80])
                except Exception as e:
                    print("Ошибка при сохранении новости:", e)

        except Exception as e:
            print("Ошибка при парсинге источника:", source.get("name"), e)

if __name__ == "__main__":
    try:
        run()
        print("\nПарсинг завершён успешно")
    except Exception as e:
        print("Ошибка в основном цикле парсера:", e)