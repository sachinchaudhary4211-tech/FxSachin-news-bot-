import requests
from datetime import datetime

WEBHOOK_URL = "https://discord.com/api/webhooks/1540641249135165490/0yIDqzxhUMMDbt2sW0MeY27gtNMo0QNOzisEbFtz_PS9p3G2hgA36zs5ZtsfnM6YEbpt"

FEED_URL = "https://www.forexfactory.com/calendar/rss"

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

    response = requests.post(WEBHOOK_URL, json=data)
    print(response.status_code)


try:
    response = requests.get(FEED_URL)
    response.raise_for_status()

    send_to_discord(
        "📈 Forex Factory Update",
        f"Forex Factory calendar checked successfully.\n\nTime: {datetime.now()}"
    )

except Exception as e:
    send_to_discord(
        "❌ Forex News Bot Error",
        str(e)
    )
