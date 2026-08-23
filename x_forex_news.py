import os
import requests

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime
from zoneinfo import ZoneInfo


# ==========================================
# SETTINGS
# ==========================================

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

CALENDAR_URL = (
    "https://nfs.faireconomy.media/"
    "ff_calendar_thisweek.json"
)

IST = ZoneInfo("Asia/Kolkata")


# ==========================================
# FONT FUNCTION
# ==========================================

def get_font(size, bold=False):

    if bold:
        path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    else:
        path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    return ImageFont.truetype(path, size)


# ==========================================
# CREATE NEWS IMAGE
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

    # ==========================================
    # HEADER
    # ==========================================

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

    # ==========================================
    # MAIN CARD
    # ==========================================

    draw.rounded_rectangle(
        [
            (40, 300),
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

    # Impact
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
        IST
    ).strftime("%b %d, %Y")

    draw.text(
        (1070, 360),
        current_date,
        font=get_font(22),
        fill=GRAY
    )

    # ==========================================
    # COUNTRY
    # ==========================================

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

    # ==========================================
    # EVENT
    # ==========================================

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

    # ==========================================
    # BOTTOM DETAILS
    # ==========================================

    sections = [
        ("TIME", time_value, "#9b8cff"),
        ("FORECAST", forecast, GREEN),
        ("PREVIOUS", previous, BLUE),
        ("IMPACT", str(impact).upper(), impact_color)
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
            f"SUCCESS: Found {len(events)} calendar event(s)."
        )

        return events

    except requests.exceptions.RequestException as error:

        print(
            f"CALENDAR ERROR: {error}"
        )

        return []

    except ValueError as error:

        print(
            f"JSON ERROR: {error}"
        )

        return []


# ==========================================
# FORMAT EVENT TIME IN IST
# ==========================================

def format_event_time(date_value):

    if not date_value:
        return "TBA"

    try:

        event_date = datetime.fromisoformat(
            str(date_value).replace(
                "Z",
                "+00:00"
            )
        )

        event_date_ist = event_date.astimezone(
            IST
        )

        return event_date_ist.strftime(
            "%I:%M %p IST"
        )

    except Exception as error:

        print(
            f"TIME FORMAT ERROR: {error}"
        )

        return "TBA"


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
            "ERROR: DISCORD_WEBHOOK_URL secret is missing."
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

    # NO ROLE PING
    data = {
        "content": (
            "🚨 **USD HIGH IMPACT NEWS**\n\n"
            f"🌍 **Country:** {country}\n"
            f"📊 **Event:** {event}\n"
            f"⏰ **Time:** {time_value}\n"
            f"📈 **Forecast:** {forecast}\n"
            f"📉 **Previous:** {previous}\n"
            f"🔴 **Impact:** {impact}"
        )
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
                f"SUCCESS: Sent to Discord -> {event}"
            )

            return True

        print(
            f"DISCORD ERROR: {response.status_code}"
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
# MAIN
# ==========================================

def main():

    print("=" * 50)
    print("FXSACHIN USD HIGH IMPACT NEWS BOT")
    print("=" * 50)

    print(
        f"Current IST time: "
        f"{datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')}"
    )

    if not WEBHOOK_URL:

        print(
            "ERROR: Discord webhook environment variable missing."
        )

        return

    print(
        "SUCCESS: Discord webhook environment variable found."
    )

    events = get_forex_news()

    if not events:

        print(
            "ERROR: No calendar events found."
        )

        return

    print(
        "\nChecking USD High Impact events..."
    )

    usd_high_found = 0
    sent_count = 0

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

        # USD ONLY
        if country != "USD":
            continue

        # HIGH IMPACT ONLY
        if impact.lower() != "high":
            continue

        # Skip empty titles
        if not title:
            continue

        usd_high_found += 1

        print("-" * 50)

        print(
            f"USD HIGH EVENT FOUND: {title}"
        )

        time_value = format_event_time(
            date_value
        )

        print(
            f"Event time: {time_value}"
        )

        forecast = (
            event.get("forecast")
            or "N/A"
        )

        previous = (
            event.get("previous")
            or "N/A"
        )

        print(
            "SENDING TO DISCORD..."
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
            sent_count += 1

    print("\n" + "=" * 50)
    print("BOT SUMMARY")
    print("=" * 50)

    print(
        f"USD High Impact events found: {usd_high_found}"
    )

    print(
        f"Alerts sent to Discord: {sent_count}"
    )

    print("=" * 50)

    if sent_count == 0:

        print(
            "No alerts were sent. Check the Discord error above."
        )

    else:

        print(
            "SUCCESS: Test completed."
        )


# ==========================================
# RUN BOT
# ==========================================

if __name__ == "__main__":

    main()
