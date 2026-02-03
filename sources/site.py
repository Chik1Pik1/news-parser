import requests
from bs4 import BeautifulSoup
from dedup import make_hash

def parse_site(source):
    try:
        resp = requests.get(source["url"], timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        items = []
        selector = source.get("selector")
        if not selector:
            return items

        for a in soup.select(selector):
            title = a.get_text(strip=True)
            link = a.get("href")
            if not link or not title:
                continue
            if not link.startswith("http"):
                link = source["url"].rstrip("/") + "/" + link.lstrip("/")
            h = make_hash(title, link)

            img = a.find("img")
            media_url = img["src"] if img else None

            items.append({
                "source_id": source["id"],
                "category_id": source["category_id"],
                "title": title,
                "summary": "",
                "url": link,
                "published_at": None,
                "hash": h,
                "is_nsfw": False,
                "media_url": media_url
            })
        print(f"Найдено {len(items)} новостей на сайте: {source['name']}")
        return items
    except Exception as e:
        print(f"❌ Ошибка при парсинге сайта {source['name']}: {e}")
        return []