import feedparser
from feedgen.feed import FeedGenerator
import hashlib
import time
import requests

# Two PolitePol feeds you gave
FEEDS = [
    "https://politepaul.com/fd/sjcE9vQeC0vq.xml",
    "https://politepaul.com/fd/P9rziMVM8wgM.xml"
]

def get_identifier(entry):
    """Unique ID based on title+link."""
    title = entry.get("title", "")
    link = entry.get("link", "")
    return hashlib.md5((title + link).encode("utf-8")).hexdigest()

def fetch_and_merge():
    all_entries = []
    for url in FEEDS:
        try:
            d = feedparser.parse(requests.get(url, timeout=15).content)
            all_entries.extend(d.entries)
        except Exception as e:
            print(f"Error fetching {url}: {e}")

    # Deduplicate
    seen = set()
    unique_entries = []
    for entry in all_entries:
        ident = get_identifier(entry)
        if ident not in seen:
            seen.add(ident)
            unique_entries.append(entry)

    # Sort newest first
    unique_entries.sort(
        key=lambda e: getattr(e, "published_parsed", time.gmtime(0)),
        reverse=True
    )

    # Generate merged feed
    fg = FeedGenerator()
    fg.title("Merged Feed")
    fg.link(href="https://github.com/your-username/merged-rss", rel="alternate")
    fg.description("Merged RSS feed (duplicates removed)")

    for entry in unique_entries[:50]:  # keep latest 50
        fe = fg.add_entry()
        fe.title(entry.title)
        if "link" in entry:
            fe.link(href=entry.link)
        if "published" in entry:
            fe.pubDate(entry.published)
        if "summary" in entry:
            fe.description(entry.summary)

    fg.rss_file("feed.xml")
    print("✅ feed.xml updated")

if __name__ == "__main__":
    fetch_and_merge()
