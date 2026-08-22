import requests
from datetime import datetime

WEBHOOK_URL = "https://discord.com/api/webhooks/1540641249135165490/0yIDqzxhUMMDbt2sW0MeY27gtNMo0QNOzisEbFtz_PS9p3G2hgA36zs5ZtsfnM6YEbpt"

FEED_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"


def send_to_discord(title, description):
    data = {
        "embeds": [
            {
                "title": title,
                "description": description,
                "footer": {
                    "text": "FxSachin • Forex News"
                }
            }
        ]
    }

    requests.post(WEBHOOK_URL, json=data)


try:
    response = requests.get(
        FEED_URL,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30
    )

    response.raise_for_status()

    news = response.json()

    high_impact = [
        event for event in news
        if event.get("impact") == "High"
    ]

    if high_impact:
        event = high_impact[0]

        message = (
            f"**Country:** {event.get('country')}\n"
            f"**Event:** {event.get('title')}\n"
            f"**Time:** {event.get('date')}\n"
            f"**Impact:** {event.get('impact')}\n"
            f"**Forecast:** {event.get('forecast')}\n"
            f"**Previous:** {event.get('previous')}"
        )

        send_to_discord("🔴 HIGH IMPACT FOREX NEWS", message)

    else:
        send_to_discord(
            "📊 Forex News Update",
            "No high-impact news found."
        )

except Exception as e:
    send_to_discord(
        "❌ Forex News Bot Error",
        str(e)
    )
