import os
import json
import time
import requests
from datetime import datetime, timezone


# =========================================================
# CONFIGURATION
# =========================================================

# X/Twitter API Bearer Token
X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")

# Discord Webhook URL
DISCORD_WEBHOOK_URL = os.getenv("https://discord.com/api/webhooks/1540701416304279682/hoaYmfCMjCEdFfjRgq_XCcMLu4oHeXSBqR2G9r0kd-6MbQ0zBKl6Y8XsWMTa1OIH864o")

# Check every 60 seconds
CHECK_INTERVAL = 60


# =========================================================
# FILE TO REMEMBER SENT POSTS
# =========================================================

SENT_FILE = "sent_twitter_posts.json"


# =========================================================
# TRUSTED ACCOUNTS
# =========================================================

TRUSTED_ACCOUNTS = [
    "federalreserve",
    "USTreasury",
    "Reuters",
    "WSJ",
    "Bloomberg",
]


# =========================================================
# HIGH IMPACT KEYWORDS
# =========================================================

HIGH_IMPACT_KEYWORDS = [
    "federal reserve",
    "fomc",
    "powell",
    "interest rate",
    "rate hike",
    "rate cut",
    "emergency meeting",

    "cpi",
    "inflation",
    "nonfarm payroll",
    "nfp",
    "payrolls",
    "jobs report",
    "unemployment",
    "gdp",
    "retail sales",

    "us dollar",
    "usd",
    "dxy",
    "dollar index",

    "us treasury",
    "treasury yields",
    "bond yields",

    "tariffs",
    "sanctions",
    "trade war",
    "intervention",

    "breaking",
    "emergency",
    "war",
]


# =========================================================
# LOAD SENT POSTS
# =========================================================

def load_sent_posts():
    if not os.path.exists(SENT_FILE):
        return set()

    try:
        with open(SENT_FILE, "r", encoding="utf-8") as file:
            return set(json.load(file))

    except Exception as error:
        print(f"Error loading sent posts: {error}")
        return set()


# =========================================================
# SAVE SENT POSTS
# =========================================================

def save_sent_posts(sent_posts):
    try:
        sent_list = list(sent_posts)[-500:]

        with open(SENT_FILE, "w", encoding="utf-8") as file:
            json.dump(sent_list, file)

    except Exception as error:
        print(f"Error saving posts: {error}")


# =========================================================
# CHECK IF POST IS HIGH IMPACT
# =========================================================

def is_high_impact(text):
    text_lower = text.lower()

    matches = []

    for keyword in HIGH_IMPACT_KEYWORDS:
        if keyword in text_lower:
            matches.append(keyword)

    if matches:
        return True, matches

    return False, []


# =========================================================
# BUILD X SEARCH QUERY
# =========================================================

def build_query():

    accounts_query = " OR ".join(
        [f"from:{account}" for account in TRUSTED_ACCOUNTS]
    )

    keyword_query = (
        '"Federal Reserve" OR '
        'FOMC OR '
        'Powell OR '
        '"interest rate" OR '
        '"rate hike" OR '
        '"rate cut" OR '
        'CPI OR '
        'inflation OR '
        '"Nonfarm Payroll" OR '
        'NFP OR '
        '"jobs report" OR '
        '"US dollar" OR '
        'USD OR '
        'DXY OR '
        '"Treasury yields" OR '
        'tariffs OR '
        'sanctions'
    )

    query = (
        f"(({accounts_query}) OR ({keyword_query})) "
        f"lang:en -is:retweet"
    )

    return query


# =========================================================
# GET RECENT X POSTS
# =========================================================

def get_recent_posts():

    if not X_BEARER_TOKEN:
        print("ERROR: X_BEARER_TOKEN is missing.")
        return []

    url = "https://api.x.com/2/tweets/search/recent"

    headers = {
        "Authorization": f"Bearer {X_BEARER_TOKEN}"
    }

    params = {
        "query": build_query(),
        "max_results": 20,
        "tweet.fields": "created_at,author_id",
        "expansions": "author_id",
        "user.fields": "username,name"
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=30
        )

        print(f"X API Status: {response.status_code}")

        if response.status_code != 200:
            print(response.text)
            return []

        data = response.json()

        posts = data.get("data", [])

        users = {}

        for user in data.get("includes", {}).get("users", []):
            users[user["id"]] = user

        result = []

        for post in posts:

            author = users.get(
                post.get("author_id"),
                {}
            )

            result.append({
                "id": post.get("id"),
                "text": post.get("text", ""),
                "created_at": post.get("created_at", ""),
                "username": author.get("username", "unknown"),
                "name": author.get("name", "Unknown Source")
            })

        return result

    except Exception as error:
        print(f"Error getting X posts: {error}")
        return []


# =========================================================
# SEND TO DISCORD
# =========================================================

def send_discord_alert(post, matched_keywords):

    username = post["username"]

    post_url = f"https://x.com/{username}/status/{post['id']}"

    embed = {

        "title": "🚨 HIGH IMPACT FOREX / USD NEWS",

        "description": (
            f"**Source:** {post['name']} (@{username})\n\n"
            f"**News:**\n{post['text'][:3500]}\n\n"
            f"**Possible Market Impact:** 🔴 HIGH\n"
            f"**Currency Focus:** 🇺🇸 USD / Forex\n"
            f"**Matched Keywords:** {', '.join(matched_keywords[:5])}\n\n"
            f"🔗 [View Original X Post]({post_url})"
        ),

        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),

        "footer": {
            "text": "Forex Breaking News Bot"
        }
    }

    payload = {
        "embeds": [embed]
    }

    try:

        response = requests.post(
            DISCORD_WEBHOOK_URL,
            json=payload,
            timeout=30
        )

        print(f"Discord Status: {response.status_code}")

        if response.status_code in [200, 204]:

            print(f"SUCCESS: Sent post {post['id']}")
            return True

        print(response.text)
        return False

    except Exception as error:

        print(f"Discord error: {error}")
        return False


# =========================================================
# CHECK NEWS
# =========================================================

def check_news(sent_posts):

    print("\n----------------------------------")
    print("Checking X/Twitter forex news...")
    print("----------------------------------")

    posts = get_recent_posts()

    if not posts:
        print("No new posts found.")
        return

    # Send older posts first
    posts.reverse()

    for post in posts:

        post_id = post["id"]

        # Skip already processed posts
        if post_id in sent_posts:
            continue

        important, keywords = is_high_impact(
            post["text"]
        )

        if not important:

            print(
                f"Skipped: {post['id']} - not high impact"
            )

            sent_posts.add(post_id)
            continue

        print("\n🚨 HIGH IMPACT NEWS FOUND")
        print(f"Source: @{post['username']}")
        print(f"Text: {post['text']}")
        print(f"Keywords: {keywords}")

        success = send_discord_alert(
            post,
            keywords
        )

        if success:

            sent_posts.add(post_id)

            save_sent_posts(sent_posts)


# =========================================================
# START BOT
# =========================================================

def main():

    print("==================================")
    print("FOREX X NEWS BOT STARTED")
    print("==================================")

    if not DISCORD_WEBHOOK_URL:

        print(
            "ERROR: DISCORD_WEBHOOK_URL is missing."
        )

        return

    if not X_BEARER_TOKEN:

        print(
            "ERROR: X_BEARER_TOKEN is missing."
        )

        return

    sent_posts = load_sent_posts()

    print(
        f"Loaded {len(sent_posts)} old posts."
    )

    while True:

        try:
            check_news(sent_posts)

        except Exception as error:
            print(f"Main loop error: {error}")

        print(f"\nWaiting {CHECK_INTERVAL} seconds...")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
