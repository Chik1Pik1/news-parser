import requests
from bs4 import BeautifulSoup
from dedup import make_hash

def parse_site(source):
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
        items.append({
            "source_id": source["id"],
            "category_id": source["category_id"],
            "title": title,
            "summary": "",
            "url": link,
            "published_at": None,
            "hash": h,
            "is_nsfw": False
        })
    return items
