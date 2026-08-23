import os
import json
import hashlib
import requests

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime, timezone


# ==========================================
# SETTINGS
# ==========================================

# Discord webhook from GitHub Secret
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Discord role ID
ROLE_ID = "1540675428572987452"

# Forex Factory economic calendar feed
CALENDAR_URL = (
    "https://nfs.faireconomy.media/"
    "ff_calendar_thisweek.json"
)

# File used to prevent duplicate alerts
SENT_EVENTS_FILE = "sent_events.json"

# Alert before the event
# Bot will send USD High Impact news
# when it is within the next 90 minutes
ALERT_WINDOW_MINUTES = 90


# ==========================================
# FONT FUNCTION
# ==========================================

def get_font(size, bold=False):

    if bold:
        path = (
            "/usr/share/fonts/truetype/"
            "dejavu/DejaVuSans-Bold.ttf"
        )
    else:
        path = (
            "/usr/share/fonts/truetype/"
            "dejavu/DejaVuSans.ttf"
        )

    return ImageFont.truetype(path, size)


# ==========================================
# CREATE FOREX NEWS IMAGE
# ==========================================

def create_news_image(
    country,
    event,
    time_value,
    forecast,
    previous,
    impact
):

    WIDTH = 1400
    HEIGHT = 900

    image = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        "#0b1019"
    )

    draw = ImageDraw.Draw(image)

    WHITE = "#f2f4f8"
    GRAY = "#9da7b8"
    RED = "#ff3131"
    BLUE = "#3d8cff"
    GREEN = "#55c74d"
    ORANGE = "#ffb020"
    DARK = "#111927"
    BORDER = "#2a3445"

    # Header
    draw.rectangle(
        [(0, 0), (WIDTH, 280)],
        fill="#07111f"
    )

    for x in range(0, WIDTH, 60):

        draw.line(
            [(x, 0), (x + 100, 280)],
            fill="#101b2b",
            width=1
        )

    # Red section
    draw.rectangle(
        [(1050, 0), (WIDTH, 280)],
        fill="#21080d"
    )

    # Candlestick decoration
    candle_x = 1080

    candle_heights = [
        70,
        120,
        50,
        150,
        90,
        180
    ]

    for i, height in enumerate(candle_heights):

        x = candle_x + (i * 50)
        y = 230 - height

        draw.line(
            [
                (x + 12, y - 20),
                (x + 12, y + height + 20)
            ],
            fill=RED,
            width=3
        )

        draw.rectangle(
            [
                (x, y),
                (x + 24, y + height)
            ],
            fill=RED
        )

    # Logo
    draw.text(
        (590, 50),
        "FXSACHIN",
        font=get_font(38, True),
        fill=WHITE
    )

    draw.text(
        (390, 100),
        "FOREX",
        font=get_font(100, True),
        fill=WHITE
    )

    draw.text(
        (750, 100),
        "NEWS",
        font=get_font(100, True),
        fill=RED
    )

    draw.text(
        (470, 220),
        "STAY AHEAD. TRADE SMART.",
        font=get_font(28),
        fill=GRAY
    )

    # Main card
    card_top = 300

    draw.rounded_rectangle(
        [
            (40, card_top),
            (1360, 850)
        ],
        radius=30,
        fill=DARK,
        outline=BORDER,
        width=3
    )

    # Impact color
    impact_lower = str(impact).lower()

    if impact_lower == "high":
        impact_color = RED

    elif impact_lower == "medium":
        impact_color = ORANGE

    elif impact_lower == "low":
        impact_color = GREEN

    else:
        impact_color = BLUE

    # Impact header
    draw.ellipse(
        [
            (80, 350),
            (130, 400)
        ],
        fill=impact_color
    )

    draw.text(
        (160, 350),
        f"{str(impact).upper()} IMPACT",
        font=get_font(45, True),
        fill=WHITE
    )

    draw.text(
        (650, 350),
        "FOREX NEWS",
        font=get_font(45, True),
        fill=RED
    )

    current_date = datetime.now(
        timezone.utc
    ).strftime("%b %d, %Y")

    draw.text(
        (1070, 360),
        current_date,
        font=get_font(22),
        fill=GRAY
    )

    # Country box
    draw.rounded_rectangle(
        [
            (80, 440),
            (1320, 550)
        ],
        radius=20,
        fill="#0d1522",
        outline=BORDER,
        width=2
    )

    draw.text(
        (130, 450),
        str(country).upper(),
        font=get_font(45, True),
        fill=WHITE
    )

    draw.text(
        (130, 510),
        "COUNTRY / CURRENCY",
        font=get_font(18),
        fill=GRAY
    )

    # Event box
    draw.rounded_rectangle(
        [
            (80, 580),
            (1320, 690)
        ],
        radius=20,
        fill="#0d1522",
        outline=BORDER,
        width=2
    )

    draw.text(
        (130, 595),
        "EVENT",
        font=get_font(20, True),
        fill=RED
    )

    event_text = str(event)

    if len(event_text) > 45:
        event_text = event_text[:42] + "..."

    draw.text(
        (130, 630),
        event_text,
        font=get_font(38, True),
        fill=WHITE
    )

    # Bottom details
    sections = [
        ("TIME", time_value, "#9b8cff"),
        ("FORECAST", forecast, GREEN),
        ("PREVIOUS", previous, BLUE),
        (
            "IMPACT",
            str(impact).upper(),
            impact_color
        )
    ]

    start_x = 100
    box_width = 300

    for i, section in enumerate(sections):

        label = section[0]
        value = section[1]
        color = section[2]

        x = start_x + (i * box_width)

        if i > 0:

            draw.line(
                [
                    (x - 30, 720),
                    (x - 30, 820)
                ],
                fill=BORDER,
                width=2
            )

        draw.text(
            (x, 720),
            label,
            font=get_font(22, True),
            fill=color
        )

        value_color = WHITE

        if label == "IMPACT":
            value_color = impact_color

        draw.text(
            (x, 760),
            str(value),
            font=get_font(38, True),
            fill=value_color
        )

    # Footer
    draw.text(
        (540, 830),
        "FxSachin • Forex News",
        font=get_font(20),
        fill=GRAY
    )

    image_bytes = BytesIO()

    image.save(
        image_bytes,
        format="PNG"
    )

    image_bytes.seek(0)

    return image_bytes


# ==========================================
# LOAD SENT EVENTS
# ==========================================

def load_sent_events():

    if not os.path.exists(SENT_EVENTS_FILE):
        return []

    try:

        with open(
            SENT_EVENTS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception as error:

        print(
            f"WARNING: Could not load sent events: {error}"
        )

        return []


# ==========================================
# SAVE SENT EVENTS
# ==========================================

def save_sent_events(events):

    with open(
        SENT_EVENTS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            events,
            file,
            indent=4
        )


# ==========================================
# CREATE UNIQUE EVENT ID
# ==========================================

def create_event_id(event):

    event_data = (
        f"{event.get('date', '')}|"
        f"{event.get('country', '')}|"
        f"{event.get('title', '')}|"
        f"{event.get('impact', '')}"
    )

    return hashlib.md5(
        event_data.encode("utf-8")
    ).hexdigest()


# ==========================================
# GET FOREX NEWS
# ==========================================

def get_forex_news():

    headers = {
        "User-Agent": "Mozilla/5.0 FxSachinNewsBot/1.0"
    }

    try:

        response = requests.get(
            CALENDAR_URL,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        events = response.json()

        print(
            f"SUCCESS: Found {len(events)} "
            f"calendar event(s)."
        )

        return events

    except requests.exceptions.RequestException as error:

        print(
            f"Calendar request error: {error}"
        )

        return []

    except ValueError as error:

        print(
            f"Calendar JSON error: {error}"
        )

        return []


# ==========================================
# PARSE EVENT DATE
# ==========================================

def parse_event_date(date_value):

    if not date_value:
        return None

    try:

        event_date = datetime.fromisoformat(
            str(date_value).replace(
                "Z",
                "+00:00"
            )
        )

        if event_date.tzinfo is None:

            event_date = event_date.replace(
                tzinfo=timezone.utc
            )

        return event_date

    except Exception as error:

        print(
            f"DATE PARSE ERROR: "
            f"{date_value} -> {error}"
        )

        return None


# ==========================================
# FORMAT EVENT TIME
# ==========================================

def format_event_time(date_value):

    event_date = parse_event_date(
        date_value
    )

    if not event_date:
        return "TBA"

    return event_date.strftime(
        "%I:%M %p UTC"
    )


# ==========================================
# CHECK ALERT WINDOW
# ==========================================

def get_minutes_until_event(date_value):

    event_date = parse_event_date(
        date_value
    )

    if not event_date:
        return None

    now = datetime.now(
        timezone.utc
    )

    minutes_until = (
        event_date - now
    ).total_seconds() / 60

    return minutes_until


# ==========================================
# SEND TO DISCORD
# ==========================================

def send_to_discord(
    country,
    event,
    time_value,
    forecast,
    previous,
    impact
):

    if not WEBHOOK_URL:

        print(
            "ERROR: DISCORD_WEBHOOK_URL missing."
        )

        return False

    image_bytes = create_news_image(
        country,
        event,
        time_value,
        forecast,
        previous,
        impact
    )

    files = {
        "file": (
            "forex_news.png",
            image_bytes,
            "image/png"
        )
    }

    data = {
        "content": (
            f"<@&{ROLE_ID}>\n\n"
            "🚨 **HIGH IMPACT USD NEWS ALERT**\n\n"
            f"🌍 **Country:** {country}\n"
            f"📊 **Event:** {event}\n"
            f"⏰ **Time:** {time_value}\n"
            f"📈 **Forecast:** {forecast}\n"
            f"📉 **Previous:** {previous}\n"
            f"🔴 **Impact:** {impact}"
        ),

        "allowed_mentions": {
            "roles": [ROLE_ID]
        }
    }

    try:

        response = requests.post(
            WEBHOOK_URL,
            data=data,
            files=files,
            timeout=30
        )

        if response.status_code in [200, 204]:

            print(
                f"SUCCESS: Alert sent to Discord: "
                f"{event}"
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

    except requests.exceptions.RequestException as error:

        print(
            f"DISCORD EXCEPTION: {error}"
        )

        return False


# ==========================================
# MAIN BOT
# ==========================================

def main():

    print(
        "========================================"
    )

    print(
        "Fetching Forex Factory calendar..."
    )

    print(
        "========================================"
    )

    print(
        f"Current UTC time: "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"
    )

    print(
        f"Alert window: "
        f"{ALERT_WINDOW_MINUTES} minutes"
    )

    if not WEBHOOK_URL:

        print(
            "ERROR: DISCORD_WEBHOOK_URL missing."
        )

        return

    print(
        "SUCCESS: Discord webhook environment "
        "variable found."
    )

    events = get_forex_news()

    if not events:

        print(
            "No calendar events found."
        )

        return

    sent_events = load_sent_events()
    sent_set = set(sent_events)

    print(
        f"Previously sent events stored: "
        f"{len(sent_set)}"
    )

    new_sent_events = []

    usd_high_found = 0
    skipped_time = 0
    skipped_duplicate = 0
    sent_count = 0

    print(
        "\nChecking calendar events...\n"
    )

    for event in events:

        impact = str(
            event.get("impact", "")
        ).strip()

        country = str(
            event.get("country", "")
        ).strip().upper()

        title = str(
            event.get("title", "")
        ).strip()

        date_value = event.get(
            "date",
            ""
        )

        # USD only
        if country != "USD":
            continue

        # High impact only
        if impact.lower() != "high":
            continue

        if not title:

            print(
                "SKIPPED: USD High Impact event "
                "has no title."
            )

            continue

        usd_high_found += 1

        minutes_until = get_minutes_until_event(
            date_value
        )

        print(
            "----------------------------------------"
        )

        print(
            f"USD HIGH EVENT: {title}"
        )

        print(
            f"Event date: {date_value}"
        )

        print(
            f"Event time: "
            f"{format_event_time(date_value)}"
        )

        if minutes_until is None:

            print(
                "SKIPPED: Could not read event date."
            )

            skipped_time += 1

            continue

        print(
            f"Minutes until event: "
            f"{minutes_until:.2f}"
        )

        # Event already happened
        if minutes_until < 0:

            print(
                "SKIPPED: Event has already passed."
            )

            skipped_time += 1

            continue

        # Event is too far away
        if minutes_until > ALERT_WINDOW_MINUTES:

            print(
                f"SKIPPED: Event is more than "
                f"{ALERT_WINDOW_MINUTES} minutes away."
            )

            skipped_time += 1

            continue

        event_id = create_event_id(
            event
        )

        # Skip already sent event
        if event_id in sent_set:

            print(
                "SKIPPED: This event was already sent."
            )

            skipped_duplicate += 1

            continue

        print(
            "EVENT QUALIFIES FOR DISCORD ALERT."
        )

        time_value = format_event_time(
            date_value
        )

        forecast = (
            event.get("forecast")
            or "N/A"
        )

        previous = (
            event.get("previous")
            or "N/A"
        )

        success = send_to_discord(
            country=country,
            event=title,
            time_value=time_value,
            forecast=forecast,
            previous=previous,
            impact=impact
        )

        if success:

            new_sent_events.append(
                event_id
            )

            sent_set.add(
                event_id
            )

            sent_count += 1

    # Save sent events
    if new_sent_events:

        sent_events.extend(
            new_sent_events
        )

        # Keep only latest 500 event IDs
        sent_events = sent_events[-500:]

        save_sent_events(
            sent_events
        )

    print(
        "\n========================================"
    )

    print(
        "BOT SUMMARY"
    )

    print(
        "========================================"
    )

    print(
        f"USD High Impact events found: "
        f"{usd_high_found}"
    )

    print(
        f"Skipped because of time: "
        f"{skipped_time}"
    )

    print(
        f"Skipped because already sent: "
        f"{skipped_duplicate}"
    )

    print(
        f"Alerts successfully sent: "
        f"{sent_count}"
    )

    if sent_count == 0:

        print(
            "No new USD High Impact events "
            "were sent during this run."
        )

    print(
        "========================================"
    )


# ==========================================
# RUN BOT
# ==========================================

if __name__ == "__main__":

    main()
