import requests
from datetime import datetime

WEBHOOK_URL = "https://discord.com/api/webhooks/1540641249135165490/0yIDqzxhUMMDbt2sW0MeY27gtNMo0QNOzisEbFtz_PS9p3G2hgA36zs5ZtsfnM6YEbpt"

# Forex Factory RSS calendar
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

send_to_discord(
    "🚨 Forex News Bot Test",
    f"Bot is working successfully! Time: {datetime.now()}"
)
