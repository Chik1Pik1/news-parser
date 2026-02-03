import requests
from bs4 import BeautifulSoup
from dedup import make_hash

def parse_site(source):
    items = []
    selector = source.get("selector")
    if not selector:
        return items

    resp = requests.get(source["url"], timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")

    for a in soup.select(selector):
        title = a.get_text(strip=True)
        link = a.get("href")
        if not link or not title:
            continue
        if not link.startswith("http"):
            link = source["url"].rstrip("/") + "/" + link.lstrip("/")

        h = make_hash(title, link)

        img_tag = a.find("img")
        image = img_tag.get("src") if img_tag else None
        video_tag = a.find("video")
        video = video_tag.get("src") if video_tag else None

        items.append({
            "source_id": source["id"],
            "category_id": source["category_id"],
            "title": title,
            "summary": "",
            "url": link,
            "image": image,
            "video": video,
            "published_at": None,
            "hash": h,
            "is_nsfw": source.get("is_nsfw", False)
        })

    return items