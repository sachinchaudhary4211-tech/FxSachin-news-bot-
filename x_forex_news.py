import os
import json
import hashlib
import requests
import feedparser
from datetime import datetime

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

SENT_EVENTS_FILE = "sent_events.json"

# USD / US economy / Forex high-impact keywords
HIGH_IMPACT_KEYWORDS = [
    "federal reserve",
    "fed ",
    "fomc",
    "powell",
    "interest rate",
    "rate hike",
    "rate cut",
    "cpi",
    "inflation",
    "nonfarm payroll",
    "nfp",
    "payrolls",
    "unemployment",
    "jobs report",
    "gdp",
    "pce",
    "retail sales",
    "consumer confidence",
    "usd",
    "dollar",
    "us economy",
    "u.s. economy",
    "treasury",
    "yield",
    "labor market",
    "employment"
]

# RSS news sources
RSS_FEEDS = [
    "https://feeds.reuters.com/reuters/businessNews",
    "https://feeds.reuters.com/reuters/marketsNews",
]

def load_sent_events():
    if os.path.exists(SENT_EVENTS_FILE):
        try:
            with open(SENT_EVENTS_FILE, "r", encoding="utf-8") as file:
                return set(json.load(file))
        except Exception:
            return set()

    return set()


def save_sent_events(events):
    with open(SENT_EVENTS_FILE, "w", encoding="utf-8") as file:
        json.dump(list(events), file)


def is_high_impact_usd_news(title, summary):
    text = f"{title} {summary}".lower()

    matches = 0

    for keyword in HIGH_IMPACT_KEYWORDS:
        if keyword in text:
            matches += 1

    # Must have at least 2 relevant signals
    return matches >= 2


def send_to_discord(title, link, source):
    if not DISCORD_WEBHOOK_URL:
        print("ERROR: DISCORD_WEBHOOK_URL secret is missing.")
        return False

    message = {
        "embeds": [
            {
                "title": "🚨 HIGH IMPACT USD / FOREX NEWS",
                "description": (
                    f"**{title}**\n\n"
                    f"📈 Possible high impact on: **USD / Forex / Gold / Indices**\n"
                    f"📰 Source: {source}\n"
                    f"🔗 {link}"
                ),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        ]
    }

    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL,
            json=message,
            timeout=20
        )

        if response.status_code in [200, 204]:
            print("Sent to Discord successfully.")
            return True

        print("Discord error:", response.status_code)
        print(response.text)
        return False

    except Exception as error:
        print("Discord request failed:", error)
        return False


def main():
    print("Checking HIGH IMPACT USD and Forex news...")

    sent_events = load_sent_events()

    posts_found = 0
    high_impact_found = 0
    newly_sent = 0

    for feed_url in RSS_FEEDS:
        print(f"\nChecking feed: {feed_url}")

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:30]:
                posts_found += 1

                title = entry.get("title", "")
                summary = entry.get("summary", "")
                link = entry.get("link", "")

                if not title or not link:
                    continue

                if not is_high_impact_usd_news(title, summary):
                    continue

                high_impact_found += 1

                event_id = hashlib.sha256(
                    link.encode("utf-8")
                ).hexdigest()

                if event_id in sent_events:
                    print("Already sent:", title)
                    continue

                print("\nHIGH IMPACT USD NEWS FOUND:")
                print(title)

                if send_to_discord(title, link, "Reuters"):
                    sent_events.add(event_id)
                    newly_sent += 1

        except Exception as error:
            print("Feed error:", error)

    save_sent_events(sent_events)

    print("\n==============================")
    print("Posts checked:", posts_found)
    print("High impact USD news:", high_impact_found)
    print("New alerts sent:", newly_sent)
    print("Finished.")
    print("==============================")


if __name__ == "__main__":
    main()
