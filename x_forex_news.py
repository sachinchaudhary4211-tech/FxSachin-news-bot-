import os
import json
import hashlib
import html
import requests
import feedparser

from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import quote_plus


# =========================================================
# SETTINGS
# =========================================================

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

CALENDAR_URL = (
    "https://nfs.faireconomy.media/"
    "ff_calendar_thisweek.json"
)

SENT_EVENTS_FILE = "sent_events.json"

IST = ZoneInfo("Asia/Kolkata")

REQUEST_TIMEOUT = 30


# =========================================================
# IMPORTANT ECONOMIC EVENTS
# =========================================================

# Only these important USD events will be sent.
# This prevents random high-impact events from spamming Discord.

IMPORTANT_ECONOMIC_KEYWORDS = [

    "non-farm employment change",
    "nonfarm employment change",
    "non-farm payroll",
    "nonfarm payroll",
    "nfp",

    "unemployment rate",

    "cpi",
    "consumer price index",

    "core cpi",

    "pce price index",
    "core pce",

    "fomc",
    "federal funds rate",
    "interest rate decision",
    "rate statement",

    "fomc press conference",

    "powell speaks",
    "fed chair",
    "federal reserve chair",
    "fed chairman",

    "gdp",
    "gross domestic product",

    "retail sales",

    "employment change",

    "average hourly earnings"
]


# =========================================================
# BREAKING NEWS SEARCH QUERIES
# =========================================================

BREAKING_NEWS_QUERIES = [

    # Trump market-moving actions
    (
        "Trump "
        "(tariffs OR sanctions OR Iran OR China OR war "
        "OR military OR Fed OR emergency)"
    ),

    # Iran / Middle East
    (
        "Iran "
        "(attack OR war OR strike OR Israel OR US "
        "OR sanctions OR nuclear OR military OR oil)"
    ),

    # Major geopolitical market events
    (
        "(war OR military strike OR sanctions OR nuclear "
        "OR ceasefire OR attack) "
        "(United States OR Iran OR Israel)"
    ),

    # Oil / Middle East market shocks
    (
        "(Strait of Hormuz OR oil supply OR oil shock) "
        "(Iran OR war OR attack OR military)"
    ),

    # Major tariff shocks
    (
        "(Trump OR United States) "
        "(tariff OR trade war) "
        "(China OR global markets)"
    )
]


# =========================================================
# STRONG BREAKING NEWS WORDS
# =========================================================

STRONG_BREAKING_KEYWORDS = [

    "attack",
    "attacks",
    "attacked",

    "strike",
    "strikes",
    "struck",

    "war",
    "warfare",

    "military action",
    "military strike",

    "missile",
    "missiles",

    "bomb",
    "bombing",

    "sanction",
    "sanctions",

    "tariff",
    "tariffs",

    "trade war",

    "nuclear",

    "ceasefire",

    "emergency",

    "mobilization",

    "blockade",

    "strait of hormuz",

    "oil supply",

    "oil shock",

    "invasion",

    "invade",

    "retaliation",

    "retaliate"
]


# =========================================================
# IMPORTANT PEOPLE / COUNTRIES
# =========================================================

BREAKING_TOPIC_KEYWORDS = [

    "trump",

    "iran",

    "israel",

    "united states",
    "u.s.",
    "us military",

    "china",

    "russia",

    "middle east"
]


# =========================================================
# LOAD SENT ITEMS
# =========================================================

def load_sent_items():

    if not os.path.exists(SENT_EVENTS_FILE):

        return []

    try:

        with open(
            SENT_EVENTS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):

                return data

            return []

    except Exception as error:

        print(
            f"WARNING: Could not load sent items: {error}"
        )

        return []


# =========================================================
# SAVE SENT ITEMS
# =========================================================

def save_sent_items(items):

    try:

        # Keep only the newest 1000 IDs.
        items = items[-1000:]

        with open(
            SENT_EVENTS_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                items,
                file,
                indent=4
            )

        print(
            f"SUCCESS: Saved {len(items)} sent IDs."
        )

    except Exception as error:

        print(
            f"ERROR: Could not save sent items: {error}"
        )


# =========================================================
# CREATE UNIQUE ID
# =========================================================

def create_unique_id(text):

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


# =========================================================
# FORMAT EVENT TIME
# =========================================================

def format_event_time(date_value):

    if not date_value:

        return "TBA"

    try:

        date_text = str(date_value).replace(
            "Z",
            "+00:00"
        )

        event_date = datetime.fromisoformat(
            date_text
        )

        event_date_ist = event_date.astimezone(
            IST
        )

        return event_date_ist.strftime(
            "%d %b %Y • %I:%M %p IST"
        )

    except Exception as error:

        print(
            f"TIME FORMAT ERROR: {error}"
        )

        return str(date_value)


# =========================================================
# CHECK IMPORTANT ECONOMIC EVENT
# =========================================================

def is_important_economic_event(title):

    title_lower = str(title).lower()

    for keyword in IMPORTANT_ECONOMIC_KEYWORDS:

        if keyword in title_lower:

            return True

    return False


# =========================================================
# GET FOREX FACTORY CALENDAR
# =========================================================

def get_forex_calendar():

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "FxSachinMarketNewsBot/1.0"
        )
    }

    try:

        print(
            "Fetching Forex Factory calendar..."
        )

        response = requests.get(
            CALENDAR_URL,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        events = response.json()

        print(
            f"SUCCESS: Found {len(events)} "
            f"calendar event(s)."
        )

        return events

    except Exception as error:

        print(
            f"FOREX CALENDAR ERROR: {error}"
        )

        return []


# =========================================================
# CLEAN HTML
# =========================================================

def clean_text(text):

    if not text:

        return ""

    text = html.unescape(
        str(text)
    )

    text = text.replace(
        "<br>",
        " "
    )

    text = text.replace(
        "<br/>",
        " "
    )

    return text.strip()


# =========================================================
# CHECK BREAKING NEWS IMPORTANCE
# =========================================================

def is_market_moving_breaking_news(
    title,
    summary
):

    text = (
        f"{title} {summary}"
    ).lower()

    strong_count = 0

    for keyword in STRONG_BREAKING_KEYWORDS:

        if keyword in text:

            strong_count += 1

    topic_found = False

    for keyword in BREAKING_TOPIC_KEYWORDS:

        if keyword in text:

            topic_found = True

            break

    # Must contain at least one important
    # geopolitical / market-moving topic.
    if not topic_found:

        return False

    # Require strong market-moving language.
    if strong_count < 1:

        return False

    return True


# =========================================================
# GET GOOGLE NEWS RSS
# =========================================================

def get_breaking_news():

    all_articles = []

    for search_query in BREAKING_NEWS_QUERIES:

        try:

            encoded_query = quote_plus(
                search_query
            )

            rss_url = (
                "https://news.google.com/rss/search"
                f"?q={encoded_query}"
                "&hl=en-US"
                "&gl=US"
                "&ceid=US:en"
            )

            print(
                f"Checking breaking news query: "
                f"{search_query}"
            )

            feed = feedparser.parse(
                rss_url
            )

            for entry in feed.entries:

                title = clean_text(
                    entry.get(
                        "title",
                        ""
                    )
                )

                summary = clean_text(
                    entry.get(
                        "summary",
                        ""
                    )
                )

                link = entry.get(
                    "link",
                    ""
                )

                published = entry.get(
                    "published",
                    ""
                )

                source = ""

                if "source" in entry:

                    try:

                        source = entry.source.get(
                            "title",
                            ""
                        )

                    except Exception:

                        source = ""

                if not title:

                    continue

                all_articles.append({

                    "title": title,
                    "summary": summary,
                    "link": link,
                    "published": published,
                    "source": source

                })

        except Exception as error:

            print(
                f"BREAKING NEWS ERROR: {error}"
            )

    print(
        f"SUCCESS: Found {len(all_articles)} "
        f"breaking news article(s)."
    )

    return all_articles


# =========================================================
# SEND ECONOMIC NEWS TO DISCORD
# =========================================================

def send_economic_news(
    title,
    event_time,
    forecast,
    previous
):

    content = (
        "🚨 **MAJOR MARKET NEWS**\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🇺🇸 **USD EVENT:** {title}\n\n"
        f"⏰ **Time:** {event_time}\n"
        f"📊 **Forecast:** {forecast}\n"
        f"📈 **Previous:** {previous}\n\n"
        "🎯 **Potentially important for:**\n"
        "🥇 Gold (XAUUSD)\n"
        "₿ Bitcoin (BTC)\n"
        "💵 USD / Forex\n\n"
        "⚠️ High market volatility possible."
    )

    return send_discord_message(
        content
    )


# =========================================================
# SEND BREAKING NEWS TO DISCORD
# =========================================================

def send_breaking_news(
    title,
    source,
    published,
    link
):

    content = (
        "🚨🚨 **BREAKING MARKET NEWS** 🚨🚨\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📰 **{title}**\n\n"
    )

    if source:

        content += (
            f"🏢 **Source:** {source}\n"
        )

    if published:

        content += (
            f"🕒 **Published:** {published}\n"
        )

    content += (
        "\n🎯 **Possible market impact:**\n"
        "🥇 Gold (XAUUSD)\n"
        "₿ Bitcoin (BTC)\n"
        "🛢 Oil\n"
        "💵 USD / Forex\n\n"
        "⚠️ Check market reaction immediately."
    )

    if link:

        content += (
            f"\n\n🔗 {link}"
        )

    return send_discord_message(
        content
    )


# =========================================================
# SEND MESSAGE TO DISCORD
# =========================================================

def send_discord_message(content):

    if not WEBHOOK_URL:

        print(
            "ERROR: DISCORD_WEBHOOK_URL "
            "secret is missing."
        )

        return False

    try:

        response = requests.post(
            WEBHOOK_URL,
            json={
                "content": content
            },
            timeout=REQUEST_TIMEOUT
        )

        if response.status_code in [

            200,
            204

        ]:

            print(
                "SUCCESS: Discord message sent."
            )

            return True

        print(
            f"DISCORD ERROR: "
            f"{response.status_code}"
        )

        print(
            response.text
        )

        return False

    except Exception as error:

        print(
            f"DISCORD EXCEPTION: {error}"
        )

        return False


# =========================================================
# CHECK IMPORTANT ECONOMIC NEWS
# =========================================================

def check_economic_news(sent_items):

    print(
        "\n========================================"
    )

    print(
        "CHECKING MAJOR ECONOMIC EVENTS"
    )

    print(
        "========================================"
    )

    events = get_forex_calendar()

    sent_set = set(
        sent_items
    )

    new_ids = []

    found_count = 0
    sent_count = 0

    for event in events:

        country = str(
            event.get(
                "country",
                ""
            )
        ).upper().strip()

        impact = str(
            event.get(
                "impact",
                ""
            )
        ).lower().strip()

        title = str(
            event.get(
                "title",
                ""
            )
        ).strip()

        date_value = event.get(
            "date",
            ""
        )

        # USD ONLY
        if country != "USD":

            continue

        # HIGH IMPACT ONLY
        if impact != "high":

            continue

        # IMPORTANT EVENTS ONLY
        if not is_important_economic_event(
            title
        ):

            print(
                f"FILTERED OUT: {title}"
            )

            continue

        found_count += 1

        unique_text = (
            f"ECONOMIC|"
            f"{country}|"
            f"{title}|"
            f"{date_value}"
        )

        event_id = create_unique_id(
            unique_text
        )

        print(
            f"\nIMPORTANT EVENT: {title}"
        )

        if event_id in sent_set:

            print(
                "SKIPPED: Already sent."
            )

            continue

        event_time = format_event_time(
            date_value
        )

        forecast = (
            event.get(
                "forecast"
            )
            or "N/A"
        )

        previous = (
            event.get(
                "previous"
            )
            or "N/A"
        )

        print(
            "NEW IMPORTANT EVENT FOUND."
        )

        success = send_economic_news(

            title=title,

            event_time=event_time,

            forecast=forecast,

            previous=previous

        )

        if success:

            sent_count += 1

            sent_set.add(
                event_id
            )

            new_ids.append(
                event_id
            )

    print(
        f"\nImportant economic events found: "
        f"{found_count}"
    )

    print(
        f"New economic alerts sent: "
        f"{sent_count}"
    )

    return new_ids


# =========================================================
# CHECK BREAKING NEWS
# =========================================================

def check_breaking_news(sent_items):

    print(
        "\n========================================"
    )

    print(
        "CHECKING BREAKING MARKET NEWS"
    )

    print(
        "========================================"
    )

    articles = get_breaking_news()

    sent_set = set(
        sent_items
    )

    new_ids = []

    sent_count = 0

    checked_titles = set()

    for article in articles:

        title = article.get(
            "title",
            ""
        )

        summary = article.get(
            "summary",
            ""
        )

        link = article.get(
            "link",
            ""
        )

        source = article.get(
            "source",
            ""
        )

        published = article.get(
            "published",
            ""
        )

        title_key = title.lower().strip()

        # Prevent duplicate title
        # appearing from multiple searches.
        if title_key in checked_titles:

            continue

        checked_titles.add(
            title_key
        )

        if not is_market_moving_breaking_news(

            title,
            summary

        ):

            continue

        unique_text = (
            f"BREAKING|"
            f"{title}|"
            f"{link}"
        )

        article_id = create_unique_id(
            unique_text
        )

        print(
            f"\nMARKET BREAKING NEWS: {title}"
        )

        if article_id in sent_set:

            print(
                "SKIPPED: Already sent."
            )

            continue

        success = send_breaking_news(

            title=title,

            source=source,

            published=published,

            link=link

        )

        if success:

            sent_count += 1

            sent_set.add(
                article_id
            )

            new_ids.append(
                article_id
            )

    print(
        f"\nNew breaking alerts sent: "
        f"{sent_count}"
    )

    return new_ids


# =========================================================
# MAIN
# =========================================================

def main():

    print(
        "========================================"
    )

    print(
        "FXSACHIN SMART MARKET NEWS BOT"
    )

    print(
        "========================================"
    )

    print(
        f"Current IST: "
        f"{datetime.now(IST).strftime('%Y-%m-%d %I:%M:%S %p IST')}"
    )

    if not WEBHOOK_URL:

        print(
            "ERROR: DISCORD_WEBHOOK_URL "
            "environment variable missing."
        )

        return

    print(
        "SUCCESS: Discord webhook secret found."
    )

    sent_items = load_sent_items()

    print(
        f"Previously sent items: "
        f"{len(sent_items)}"
    )

    # =============================================
    # ECONOMIC NEWS
    # =============================================

    economic_new_ids = check_economic_news(
        sent_items
    )

    # Add new economic IDs immediately
    # so breaking-news checking also knows them.
    sent_items.extend(
        economic_new_ids
    )

    # =============================================
    # BREAKING NEWS
    # =============================================

    breaking_new_ids = check_breaking_news(
        sent_items
    )

    sent_items.extend(
        breaking_new_ids
    )

    # =============================================
    # SAVE
    # =============================================

    save_sent_items(
        sent_items
    )

    print(
        "\n========================================"
    )

    print(
        "FINAL SUMMARY"
    )

    print(
        "========================================"
    )

    print(
        f"Economic alerts sent: "
        f"{len(economic_new_ids)}"
    )

    print(
        f"Breaking alerts sent: "
        f"{len(breaking_new_ids)}"
    )

    print(
        f"Total alerts sent: "
        f"{len(economic_new_ids) + len(breaking_new_ids)}"
    )

    print(
        "========================================"
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()
