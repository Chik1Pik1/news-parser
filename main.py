from db import get_enabled_sources, save_news
from sources.rss import parse_rss
from sources.site import parse_site
from sources.telegram import parse_telegram

def run():
    sources = get_enabled_sources()
    for source in sources:
        print(f"Парсим: {source['name']} ({source['type']})")
        items = []
        if source["type"] == "rss":
            items = parse_rss(source)
        elif source["type"] == "site":
            items = parse_site(source)
        elif source["type"] == "telegram":
            items = parse_telegram(source)
        else:
            print("Неизвестный тип источника:", source["type"])
            continue
        for item in items:
            save_news(item)
            print("Сохранили:", item["title"][:80])

if __name__ == "__main__":
    run()
