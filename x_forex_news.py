import os
import json
import hashlib
import re
from datetime import datetime, timezone

import requests
import feedparser


# ==================================================
# CONFIGURATION
# ==================================================

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

SENT_EVENTS_FILE = "sent_events.json"

# Market banner shown in Discord
BANNER_URL = (
    "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3"
    "?auto=format&fit=crop&w=1600&q=80"
)


# ==================================================
# RSS FEEDS
# ==================================================

RSS_FEEDS = [
    {
        "name": "ForexLive",
        "url": "https://www.forexlive.com/feed/"
    },
    {
        "name": "InvestingLive",
        "url": "https://investinglive.com/feed/"
    },
    {
        "name": "Myfxbook Forex News",
        "url": "https://www.myfxbook.com/rss/forex-news"
    }
]


# ==================================================
# HIGH IMPACT USD / US MARKET EVENTS
# ==================================================

HIGH_IMPACT_KEYWORDS = [

    # Federal Reserve
    "federal reserve",
    "fomc",
    "jerome powell",
    "powell",
    "fed chair",
    "fed officials",
    "fed decision",

    # Interest rates
    "interest rate",
    "rate decision",
    "rate hike",
    "rate cut",
    "monetary policy",

    # Inflation
    "cpi",
    "consumer price index",
    "inflation",
    "core inflation",
    "pce",
    "core pce",
    "ppi",
    "producer price",

    # Employment
    "nonfarm payroll",
    "non-farm payroll",
    "nfp",
    "payrolls",
    "jobs report",
    "employment report",
    "unemployment",
    "jobless claims",
    "labor market",

    # Major US economic data
    "gdp",
    "retail sales",
    "durable goods",
    "consumer confidence",
    "economic growth",
    "recession",

    # USD and bond markets
    "us dollar",
    "u.s. dollar",
    "dollar index",
    "dxy",
    "treasury yields",
    "treasury yield",
    "bond yields",

    # Major market events
    "market intervention",
    "currency intervention",
    "emergency",
    "government shutdown",
    "tariffs",
    "trade war",
]


# ==================================================
# USD / US CONTEXT KEYWORDS
# ==================================================

USD_CONTEXT_KEYWORDS = [

    "usd",
    "dollar",
    "u.s.",
    "us ",
    "united states",
    "america",
    "american",

    "federal reserve",
    "fomc",
    "powell",
    "fed",

    "treasury",
    "washington"
]


# ==================================================
# VERY IMPORTANT / BREAKING KEYWORDS
# ==================================================

BREAKING_KEYWORDS = [

    "breaking",
    "urgent",
    "unexpected",
    "surprise",
    "shocks",
    "emergency",
    "intervention",
    "major",
    "crisis"
]


# ==================================================
# LOAD SENT EVENTS
# ==================================================

def load_sent_events():

    if not os.path.exists(SENT_EVENTS_FILE):
        return set()

    try:
        with open(
            SENT_EVENTS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return set(data)

    except Exception as error:
        print("Load error:", error)

    return set()


# ==================================================
# SAVE SENT EVENTS
# ==================================================

def save_sent_events(events):

    # Keep only latest 1000 events
    events = list(events)[-1000:]

    with open(
        SENT_EVENTS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            events,
            file,
            indent=2
        )


# ==================================================
# CLEAN RSS HTML
# ==================================================

def clean_text(text):

    if not text:
        return ""

    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ==================================================
# FIND KEYWORD MATCHES
# ==================================================

def find_matches(text, keywords):

    text = text.lower()

    matches = []

    for keyword in keywords:

        if keyword.lower() in text:
            matches.append(keyword)

    return matches


# ==================================================
# CHECK HIGH IMPACT USD NEWS
# ==================================================

def is_high_impact_usd_news(title, summary):

    text = f"{title} {summary}".lower()

    impact_matches = find_matches(
        text,
        HIGH_IMPACT_KEYWORDS
    )

    usd_matches = find_matches(
        text,
        USD_CONTEXT_KEYWORDS
    )

    breaking_matches = find_matches(
        text,
        BREAKING_KEYWORDS
    )

    # Must have at least one major economic event
    if len(impact_matches) == 0:
        return False, [], []

    # If Fed/FOMC/Powell/Treasury is mentioned,
    # automatically relevant to USD
    direct_usd_events = [
        "federal reserve",
        "fomc",
        "jerome powell",
        "powell",
        "fed chair",
        "fed officials",
        "fed decision",
        "interest rate",
        "rate decision",
        "treasury yields",
        "treasury yield"
    ]

    direct_match = any(
        event in text
        for event in direct_usd_events
    )

    # Otherwise require USD/US context
    if not direct_match and len(usd_matches) == 0:
        return False, [], []

    # Strong market-moving news:
    # 2+ high impact keywords
    # OR 1 major keyword + breaking signal
    high_impact = (
        len(impact_matches) >= 2
        or (
            len(impact_matches) >= 1
            and len(breaking_matches) >= 1
        )
        or direct_match
    )

    if not high_impact:
        return False, [], []

    return True, impact_matches, breaking_matches


# ==================================================
# CREATE SHORT KEY POINTS
# ==================================================

def get_key_points(title, summary):

    text = clean_text(summary)

    if not text:
        text = title

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    points = []

    for sentence in sentences:

        sentence = sentence.strip()

        if len(sentence) < 30:
            continue

        # Avoid extremely long points
        if len(sentence) > 220:
            sentence = sentence[:217] + "..."

        points.append(sentence)

        if len(points) == 3:
            break

    # Always show something
    if not points:
        points = [title]

    result = ""

    for point in points:
        result += f"• {point}\n"

    return result.strip()


# ==================================================
# SEND PROFESSIONAL DISCORD ALERT
# ==================================================

def send_to_discord(
    title,
    summary,
    link,
    source,
    impact_matches
):

    if not DISCORD_WEBHOOK_URL:

        print(
            "ERROR: DISCORD_WEBHOOK_URL missing."
        )

        return False


    key_points = get_key_points(
        title,
        summary
    )


    # Keep only first 3 matched event types
    event_text = ", ".join(
        impact_matches[:3]
    )

    if not event_text:
        event_text = "Major USD Market Event"


    description = (
        "## 🚨 BREAKING USD MARKET NEWS\n\n"

        f"### {title}\n\n"

        "### 📝 KEY POINTS\n"
        f"{key_points}\n\n"

        "━━━━━━━━━━━━━━━━━━\n"

        "### 📊 MARKET IMPACT\n"
        "💵 **Currency:** USD\n"
        "🔥 **Impact:** HIGH\n"
        f"📌 **Event:** {event_text}\n\n"

        "👀 **Markets to Watch:**\n"
        "USD • Gold • Major Forex Pairs • US Indices\n\n"

        f"🔗 [Read Full News]({link})"
    )


    payload = {

        "username": "USD Breaking News",

        "embeds": [

            {

                "title": "🚨 HIGH IMPACT USD ALERT",

                "description": description,

                "color": 15158332,

                "image": {
                    "url": BANNER_URL
                },

                "footer": {
                    "text": (
                        f"Source: {source} • "
                        "USD High Impact Monitor"
                    )
                },

                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat()

            }

        ]

    }


    try:

        response = requests.post(
            DISCORD_WEBHOOK_URL,
            json=payload,
            timeout=20
        )


        if response.status_code in [200, 204]:

            print(
                "SUCCESS: Alert sent to Discord."
            )

            return True


        print(
            "DISCORD ERROR:",
            response.status_code
        )

        print(
            response.text
        )

        return False


    except Exception as error:

        print(
            "DISCORD EXCEPTION:",
            error
        )

        return False


# ==================================================
# MAIN NEWS CHECK
# ==================================================

def main():

    print(
        "========================================"
    )

    print(
        "CHECKING HIGH IMPACT USD NEWS"
    )

    print(
        "========================================"
    )


    sent_events = load_sent_events()


    total_entries = 0

    matched_news = 0

    alerts_sent = 0


    for feed_info in RSS_FEEDS:


        source = feed_info["name"]

        feed_url = feed_info["url"]


        print(
            f"\nChecking {source}..."
        )


        try:


            feed = feedparser.parse(
                feed_url
            )


            print(
                f"Entries found: "
                f"{len(feed.entries)}"
            )


            for entry in feed.entries[:40]:


                total_entries += 1


                title = clean_text(
                    entry.get("title", "")
                )


                summary = clean_text(
                    entry.get(
                        "summary",
                        entry.get(
                            "description",
                            ""
                        )
                    )
                )


                link = entry.get(
                    "link",
                    ""
                ).strip()


                if not title or not link:
                    continue


                # Unique ID based on link
                event_id = hashlib.sha256(

                    link.encode(
                        "utf-8"
                    )

                ).hexdigest()


                # Already sent
                if event_id in sent_events:
                    continue


                matched, impact_matches, breaking_matches = (
                    is_high_impact_usd_news(
                        title,
                        summary
                    )
                )


                if not matched:
                    continue


                matched_news += 1


                print(
                    "\n🚨 HIGH IMPACT USD NEWS FOUND"
                )

                print(
                    f"Title: {title}"
                )

                print(
                    f"Impact keywords: {impact_matches}"
                )


                success = send_to_discord(

                    title=title,

                    summary=summary,

                    link=link,

                    source=source,

                    impact_matches=impact_matches

                )


                if success:

                    sent_events.add(
                        event_id
                    )

                    alerts_sent += 1


        except Exception as error:


            print(
                f"ERROR checking {source}:",
                error
            )


    save_sent_events(
        sent_events
    )


    print(
        "\n========================================"
    )

    print(
        "CHECK COMPLETE"
    )

    print(
        "========================================"
    )

    print(
        f"Total articles checked: "
        f"{total_entries}"
    )

    print(
        f"High impact USD news found: "
        f"{matched_news}"
    )

    print(
        f"Discord alerts sent: "
        f"{alerts_sent}"
    )


# ==================================================
# START
# ==================================================

if __name__ == "__main__":
    main()
