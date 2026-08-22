import os
import json
import requests
from datetime import datetime, timezone


# ==========================================
# CONFIGURATION
# ==========================================

X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

SENT_FILE = "sent_events.json"

# Maximum posts to request
MAX_RESULTS = 20


# ==========================================
# X SEARCH QUERY
# ==========================================

QUERY = """
(
USD OR "US Dollar" OR forex OR "foreign exchange"
OR FederalReserve OR "Federal Reserve" OR Fed
OR FOMC OR Powell
OR CPI OR inflation
OR NFP OR payrolls OR "Nonfarm Payrolls"
OR "interest rates"
OR "US jobs"
OR "unemployment rate"
OR GDP OR PCE
OR "retail sales"
OR "consumer confidence"
OR "Treasury yields"
OR recession
OR "rate hike"
OR "rate cut"
)
-lang:und -is:retweet
"""


# ==========================================
# CHECK ENVIRONMENT VARIABLES
# ==========================================

if not X_BEARER_TOKEN:
    raise ValueError("X_BEARER_TOKEN is missing.")

if not DISCORD_WEBHOOK_URL:
    raise ValueError("DISCORD_WEBHOOK_URL is missing.")


# ==========================================
# LOAD SENT POSTS
# ==========================================

def load_sent_posts():
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


# ==========================================
# SAVE SENT POSTS
# ==========================================

def save_sent_posts(sent_posts):

    # Keep only the latest 1000 IDs
    sent_posts = sent_posts[-1000:]

    with open(SENT_FILE, "w", encoding="utf-8") as file:
        json.dump(sent_posts, file, indent=2)


# ==========================================
# GET X POSTS
# ==========================================

def get_x_posts():

    url = "https://api.x.com/2/tweets/search/recent"

    headers = {
        "Authorization": f"Bearer {X_BEARER_TOKEN}"
    }

    params = {
        "query": QUERY,
        "max_results": MAX_RESULTS,
        "tweet.fields": "created_at,author_id,public_metrics",
        "expansions": "author_id",
        "user.fields": "username,name,verified"
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=30
    )

    if response.status_code != 200:

        print("X API ERROR:")
        print(response.status_code)
        print(response.text)

        return []

    data = response.json()

    tweets = data.get("data", [])
    users = data.get("includes", {}).get("users", [])

    users_dict = {
        user["id"]: user
        for user in users
    }

    results = []

    for tweet in tweets:

        author_id = tweet.get("author_id")

        user = users_dict.get(
            author_id,
            {}
        )

        username = user.get(
            "username",
            "unknown"
        )

        results.append({
            "id": tweet.get("id"),
            "text": tweet.get("text", ""),
            "username": username,
            "name": user.get("name", username),
            "created_at": tweet.get("created_at", "")
        })

    return results


# ==========================================
# HIGH IMPACT FILTER
# ==========================================

def is_high_impact(text):

    text = text.lower()

    high_impact_words = [

        "federal reserve",
        "fomc",
        "jerome powell",
        "powell",

        "interest rate",
        "interest rates",
        "rate hike",
        "rate cut",

        "inflation",
        "cpi",
        "pce",

        "nonfarm payroll",
        "payrolls",
        "nfp",

        "unemployment",
        "jobs report",
        "employment report",

        "gdp",

        "recession",

        "us dollar",
        "usd",

        "treasury yield",
        "bond yields",

        "emergency rate",

        "fed chair",

        "hawkish",
        "dovish",

        "retail sales"
    ]

    for word in high_impact_words:

        if word in text:
            return True

    return False


# ==========================================
# SEND DISCORD MESSAGE
# ==========================================

def send_to_discord(post):

    tweet_id = post["id"]
    username = post["username"]
    name = post["name"]
    text = post["text"]

    tweet_url = (
        f"https://x.com/"
        f"{username}/status/"
        f"{tweet_id}"
    )

    payload = {

        "username": "Forex News Bot",

        "embeds": [
            {

                "title": "🚨 HIGH IMPACT FOREX / USD NEWS",

                "description": text[:4000],

                "url": tweet_url,

                "color": 15158332,

                "fields": [

                    {
                        "name": "Source",
                        "value": f"{name} (@{username})",
                        "inline": True
                    },

                    {
                        "name": "Market",
                        "value": "USD / Forex",
                        "inline": True
                    }

                ],

                "footer": {
                    "text": "X Forex News Monitor"
                },

                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat()

            }
        ]

    }

    response = requests.post(
        DISCORD_WEBHOOK_URL,
        json=payload,
        timeout=30
    )

    if response.status_code not in [200, 204]:

        print("DISCORD ERROR:")
        print(response.status_code)
        print(response.text)

        return False

    return True


# ==========================================
# MAIN
# ==========================================

def main():

    print("Checking X for USD and Forex news...")

    sent_posts = load_sent_posts()

    posts = get_x_posts()

    print(f"Posts found: {len(posts)}")

    new_posts = []

    for post in posts:

        post_id = post["id"]

        if post_id in sent_posts:
            continue

        text = post["text"]

        if not is_high_impact(text):
            continue

        new_posts.append(post)

    # Send oldest first
    new_posts.reverse()

    print(
        f"New high impact posts: "
        f"{len(new_posts)}"
    )

    for post in new_posts:

        print(
            f"Sending: "
            f"{post['username']}"
        )

        success = send_to_discord(post)

        if success:

            sent_posts.append(
                post["id"]
            )

    save_sent_posts(sent_posts)

    print("Finished.")


# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":
    main()
