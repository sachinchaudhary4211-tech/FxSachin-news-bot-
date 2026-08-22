import os
import json
import hashlib
import requests
import feedparser
from datetime import datetime, timezone

# ==============================
# SETTINGS
# ==============================

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

SENT_FILE = "sent_events.json"

RSS_FEEDS = [
    "https://www.forexlive.com/feed/",
    "https://www.myfxbook.com/rss/forex-news",
]

# Important Forex / USD keywords
HIGH_IMPACT_KEYWORDS = [
    # USD / Federal Reserve
    "federal reserve",
    "fed ",
    "fomc",
    "powell",
    "interest rate",
    "rate hike",
    "rate cut",
    "us inflation",
    "cpi",
    "core cpi",
    "pce",
    "nonfarm",
    "nfp",
    "payroll",
    "unemployment",
    "jobs report",
    "gdp",

    # USD / US economy
    "us dollar",
    "dollar index",
    "usd",
    "treasury",
    "bond yield",

    # Forex currencies
    "eur",
    "gbp",
    "jpy",
    "aud",
    "cad",
    "nzd",
    "chf",

    # Central banks
    "ecb",
    "bank of england",
    "boe",
    "bank of japan",
    "boj",
    "rba",
    "bank of canada",
    "boc",

    # Major Forex market events
    "currency intervention",
    "forex market",
    "fx market",
]

# Words that make a news item more important
URGENT_KEYWORDS = [
    "breaking",
    "emergency",
    "unexpected",
    "surprise",
    "urgent",
    "crisis",
    "intervention",
    "rate decision",
]


# ==============================
# LOAD SENT NEWS
# ==============================

def load_sent_news():
    if not os.path.exists(SENT_FILE):
        return []

    try:
        with open(SENT_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

            if isinstance(data, list):
                return data

            return []
    except Exception:
        return []


# ==============================
# SAVE SENT NEWS
# ==============================

def save_sent_news(sent_news):
    # Keep only latest 500 IDs
    sent_news = sent_news[-500:]

    with open(SENT_FILE, "w", encoding="utf-8") as file:
        json.dump(sent_news, file, indent=2)


# ==============================
# CREATE NEWS ID
# ==============================

def create_news_id(title, link):
    text = f"{title}|{link}"

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


# ==============================
# CHECK IMPORTANT NEWS
# ==============================

def is_high_impact(title, summary):
    text = f"{title} {summary}".lower()

    keyword_found = any(
        keyword.lower() in text
        for keyword in HIGH_IMPACT_KEYWORDS
    )

    urgent_found = any(
        keyword.lower() in text
        for keyword in URGENT_KEYWORDS
    )

    return keyword_found, urgent_found


# ==============================
# SEND TO DISCORD
# ==============================

def send_to_discord(title, summary, link, source, urgent=False):

    if not DISCORD_WEBHOOK_URL:
        print("ERROR: DISCORD_WEBHOOK_URL is missing.")
        return False

    title_prefix = "🚨 HIGH IMPACT FOREX NEWS"

    if urgent:
        title_prefix = "🔥 BREAKING FOREX NEWS"

    description = summary.strip()

    if not description:
        description = "Important Forex or USD market news detected."

    # Discord embed descriptions have limits
    description = description[:3500]

    payload = {
        "username": "Forex News Bot",
        "embeds": [
            {
                "title": f"{title_prefix}\n\n{title}",
                "description": description,
                "url": link,
                "fields": [
                    {
                        "name": "Source",
                        "value": source,
                        "inline": True
                    },
                    {
                        "name": "Time",
                        "value": datetime.now(
                            timezone.utc
                        ).strftime("%Y-%m-%d %H:%M UTC"),
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "USD & Forex Market News"
                }
            }
        ]
    }

    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL,
            json=payload,
            timeout=15
        )

        if response.status_code in [200, 204]:
            print("SUCCESS: Discord message sent.")
            return True

        print(
            "DISCORD ERROR:",
            response.status_code,
            response.text
        )

        return False

    except Exception as error:
        print("DISCORD EXCEPTION:", error)

        return False


# ==============================
# CHECK RSS FEEDS
# ==============================

def check_news():

    print("Checking free Forex RSS feeds...")

    sent_news = load_sent_news()

    new_sent_news = sent_news.copy()

    total_found = 0
    total_matched = 0
    total_sent = 0

    for feed_url in RSS_FEEDS:

        print(f"\nChecking: {feed_url}")

        try:
            feed = feedparser.parse(feed_url)

            if feed.bozo:
                print(
                    "WARNING: RSS feed may have an error."
                )

            source = feed.feed.get(
                "title",
                "Forex News"
            )

            print(
                f"Feed source: {source}"
            )

            print(
                f"Posts found: {len(feed.entries)}"
            )

            for entry in feed.entries[:20]:

                total_found += 1

                title = entry.get(
                    "title",
                    ""
                ).strip()

                link = entry.get(
                    "link",
                    ""
                ).strip()

                summary = entry.get(
                    "summary",
                    entry.get("description", "")
                )

                if not title or not link:
                    continue

                news_id = create_news_id(
                    title,
                    link
                )

                # Skip already sent news
                if news_id in sent_news:
                    continue

                matched, urgent = is_high_impact(
                    title,
                    summary
                )

                if not matched:
                    continue

                total_matched += 1

                print(
                    f"MATCHED: {title}"
                )

                success = send_to_discord(
                    title,
                    summary,
                    link,
                    source,
                    urgent
                )

                if success:
                    new_sent_news.append(
                        news_id
                    )

                    total_sent += 1

        except Exception as error:

            print(
                f"RSS ERROR for {feed_url}:",
                error
            )

    save_sent_news(
        new_sent_news
    )

    print("\n==============================")
    print("FOREX NEWS BOT FINISHED")
    print("==============================")
    print(f"Total posts checked: {total_found}")
    print(f"High-impact matches: {total_matched}")
    print(f"Discord messages sent: {total_sent}")


# ==============================
# RUN BOT
# ==============================

if __name__ == "__main__":
    check_news()
