import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime


# ==========================================
# DISCORD WEBHOOK
# ==========================================

WEBHOOK_URL = "https://discord.com/api/webhooks/1540641249135165490/0yIDqzxhUMMDbt2sW0MeY27gtNMo0QNOzisEbFtz_PS9p3G2hgA36zs5ZtsfnM6YEbpt"


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

    # Colors
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

    # Decorative lines
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

    # ==========================================
    # LOGO AND TITLE
    # ==========================================

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

    # ==========================================
    # IMPACT COLOR
    # ==========================================

    impact_lower = str(impact).lower()

    if impact_lower == "high":
        impact_color = RED

    elif impact_lower == "medium":
        impact_color = ORANGE

    elif impact_lower == "low":
        impact_color = GREEN

    else:
        impact_color = BLUE

    # Impact circle
    draw.ellipse(
        [
            (80, 350),
            (130, 400)
        ],
        fill=impact_color
    )

    # Impact text
    draw.text(
        (160, 350),
        f"{str(impact).upper()} IMPACT",
        font=get_font(45, True),
        fill=WHITE
    )

    # Forex News
    draw.text(
        (650, 350),
        "FOREX NEWS",
        font=get_font(45, True),
        fill=RED
    )

    # Current date
    current_date = datetime.now().strftime(
        "%b %d, %Y"
    )

    draw.text(
        (1070, 360),
        current_date,
        font=get_font(22),
        fill=GRAY
    )

    # ==========================================
    # COUNTRY BOX
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
    # EVENT BOX
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

    # Limit event length
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

        # Divider
        if i > 0:

            draw.line(
                [
                    (x - 30, 720),
                    (x - 30, 820)
                ],
                fill=BORDER,
                width=2
            )

        # Label
        draw.text(
            (x, 720),
            label,
            font=get_font(22, True),
            fill=color
        )

        # Value
        value_color = WHITE

        if label == "IMPACT":
            value_color = impact_color

        draw.text(
            (x, 760),
            str(value),
            font=get_font(38, True),
            fill=value_color
        )

    # ==========================================
    # FOOTER
    # ==========================================

    draw.text(
        (540, 830),
        "FxSachin • Forex News",
        font=get_font(20),
        fill=GRAY
    )

    # ==========================================
    # SAVE IMAGE TO MEMORY
    # ==========================================

    image_bytes = BytesIO()

    image.save(
        image_bytes,
        format="PNG"
    )

    image_bytes.seek(0)

    return image_bytes


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

    # Create image
    image_bytes = create_news_image(
        country,
        event,
        time_value,
        forecast,
        previous,
        impact
    )

    # Discord file
    files = {
        "file": (
            "forex_news.png",
            image_bytes,
            "image/png"
        )
    }

    # Discord message
    data = {
        "content": (
            "🚨 **FOREX NEWS ALERT**\n\n"
            f"🌍 **Country:** {country}\n"
            f"📊 **Event:** {event}\n"
            f"⏰ **Time:** {time_value}\n"
            f"📈 **Forecast:** {forecast}\n"
            f"📉 **Previous:** {previous}\n"
            f"⚠️ **Impact:** {impact}"
        )
    }

    # Send webhook
    try:

        response = requests.post(
            WEBHOOK_URL,
            data=data,
            files=files,
            timeout=20
        )

        if response.status_code in [200, 204]:

            print(
                "Successfully sent Forex News to Discord!"
            )

        else:

            print(
                f"Discord error: {response.status_code}"
            )

            print(response.text)

    except requests.exceptions.RequestException as error:

        print(
            f"Request error: {error}"
        )


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    send_to_discord(
        country="USD",
        event="Non-Farm Employment Change",
        time_value="08:30 AM",
        forecast="120K",
        previous="150K",
        impact="High"
    )
