import os
import json
import hashlib
import re
from datetime import datetime, timezone

import requests
import feedparser


# ==========================================
# SETTINGS
# ==========================================

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

SENT_EVENTS_FILE = "sent_events.json"

# Professional market banner
BANNER_URL = "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=1600&q=80"


# ==========================================
# HIGH IMPACT USD KEYWORDS
# ==========================================

USD_KEYWORDS = [
    "usd",
    "u.s. dollar",
    "us dollar",
    "dollar",
    "united states",
    "u.s.",
    "us economy",
    "u.s. economy",
    "american economy",
    "federal reserve",
    "fed",
    "fomc",
    "jerome powell",
    "powell"
]


HIGH_IMPACT_EVENTS = [
    "interest rate",
    "rate decision",
    "rate hike",
    "rate cut",
    "fomc",
    "federal reserve",
    "cpi",
    "inflation",
    "core inflation",
    "nonfarm payroll",
    "nfp",
    "payrolls",
    "unemployment",
    "jobs report",
    "employment report",
    "gdp",
    "pce",
    "retail sales",
    "consumer confidence",
    "producer prices",
    "ppi",
    "treasury yield",
    "bond yields",
    "labor market",
    "recession",
    "economic data"
]


# ==========================================
# RSS NEWS FEEDS
# ==========================================

RSS_FEEDS = [
    "https://feeds.reuters.com/reuters/businessNews",
    "https://feeds.reuters.com/reuters/marketsNews"
]


# ==========================================
# LOAD SENT NEWS
# ==========================================

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

            return set(data)

    except Exception as error:

        print("Could not load sent events:", error)

        return set()


# ==========================================
# SAVE SENT NEWS
# ==========================================

def save_sent_events(events):

    try:

        with open(
            SENT_EVENTS_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                list(events),
                file,
                indent=2
            )

    except Exception as error:

        print("Could not save sent events:", error)


# ==========================================
# CLEAN HTML TEXT
# ==========================================

def clean_text(text):

    if not text:
        return ""

    text = re.sub(
        r"<[^>]+>",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ==========================================
# GET MAIN NEWS POINTS
# ==========================================

def get_main_points(summary, title):

    text = clean_text(summary)

    if not text:
        text = title

    # Split into sentences
    sentences = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    points = []

    for sentence in sentences:

        sentence = sentence.strip()

        if len(sentence) < 20:
            continue

        # Keep only first 3 important points
        points.append(sentence)

        if len(points) >= 3:
            break

    if not points:

        points.append(title)

    # Discord bullet points
    result = ""

    for point in points:

        # Prevent extremely long Discord messages
        if len(point) > 250:
            point = point[:247] + "..."

        result += f"• {point}\n"

    return result


# ==========================================
# CHECK IF USD RELATED
# ==========================================

def is_usd_related(text):

    text = text.lower()

    matches = 0

    for keyword in USD_KEYWORDS:

        if keyword in text:

            matches += 1

    return matches >= 1


# ==========================================
# CHECK HIGH MARKET IMPACT
# ==========================================

def is_high_impact(text):

    text = text.lower()

    matches = 0

    for keyword in HIGH_IMPACT_EVENTS:

        if keyword in text:

            matches += 1

    return matches >= 1


# ==========================================
# FINAL NEWS FILTER
# ==========================================

def is_high_impact_usd_news(title, summary):

    full_text = f"{title} {summary}".lower()

    # Must be USD / US related
    usd_related = is_usd_related(full_text)

    # Must contain high-impact economic event
    high_impact = is_high_impact(full_text)

    return usd_related and high_impact


# ==========================================
# SEND ATTRACTIVE DISCORD ALERT
# ==========================================

def send_to_discord(
    title,
    summary,
    link,
    source
):

    if not DISCORD_WEBHOOK_URL:

        print(
            "ERROR: DISCORD_WEBHOOK_URL secret is missing."
        )

        return False


    main_points = get_main_points(
        summary,
        title
    )


    description = (
        "## 🚨 BREAKING MARKET NEWS\n\n"

        f"**{title}**\n\n"

        "### 📝 Main Points\n"
        f"{main_points}\n"

        "### 📊 Market Impact\n"
        "💵 **Currency:** USD\n"
        "🔥 **Impact Level:** HIGH\n"
        "📈 **Markets to Watch:** USD, Forex, Gold, Indices\n\n"

        f"🔗 **[Read Full News]({link})**"
    )


    payload = {

        "username": "USD Market Alerts",

        "avatar_url": (
            "https://cdn-icons-png.flaticon.com/512/3135/3135706.png"
        ),

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
                        "Automated USD Market Monitor"
                    )

                },

                "timestamp": (
                    datetime.now(
                        timezone.utc
                    ).isoformat()
                )

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
                "Successfully sent attractive Discord alert."
            )

            return True


        print(
            "Discord error:",
            response.status_code
        )

        print(
            response.text
        )

        return False


    except Exception as error:

        print(
            "Discord request failed:",
            error
        )

        return False


# ==========================================
# MAIN BOT
# ==========================================

def main():

    print(
        "Checking HIGH IMPACT USD market news..."
    )


    sent_events = load_sent_events()


    posts_found = 0

    usd_news_found = 0

    alerts_sent = 0


    for feed_url in RSS_FEEDS:


        print(
            f"\nChecking feed: {feed_url}"
        )


        try:


            feed = feedparser.parse(
                feed_url
            )


            print(
                f"News entries found: "
                f"{len(feed.entries)}"
            )


            # Check latest 30 news items
            for entry in feed.entries[:30]:


                posts_found += 1


                title = entry.get(
                    "title",
                    ""
                )


                summary = entry.get(
                    "summary",
                    ""
                )


                link = entry.get(
                    "link",
                    ""
                )


                if not title or not link:

                    continue


                # Check only USD + high impact
                if not is_high_impact_usd_news(
                    title,
                    summary
                ):

                    continue


                usd_news_found += 1


                # Create unique ID
                event_id = hashlib.sha256(

                    link.encode(
                        "utf-8"
                    )

                ).hexdigest()


                # Prevent duplicate news
                if event_id in sent_events:


                    print(
                        "Already sent:",
                        title
                    )


                    continue


                print(
                    "\n================================="
                )


                print(
                    "HIGH IMPACT USD NEWS FOUND"
                )


                print(
                    title
                )


                print(
                    "================================="
                )


                # Send to Discord
                success = send_to_discord(

                    title=title,

                    summary=summary,

                    link=link,

                    source="Reuters"

                )


                if success:


                    sent_events.add(
                        event_id
                    )


                    alerts_sent += 1


        except Exception as error:


            print(
                "Feed error:",
                error
            )


    # Save already sent news
    save_sent_events(
        sent_events
    )


    print(
        "\n================================="
    )


    print(
        "BOT FINISHED"
    )


    print(
        "Posts checked:",
        posts_found
    )


    print(
        "High impact USD news found:",
        usd_news_found
    )


    print(
        "New alerts sent:",
        alerts_sent
    )


    print(
        "================================="
    )


# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":

    main()
