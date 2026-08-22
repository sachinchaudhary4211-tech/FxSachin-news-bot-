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

    # Create background
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

    # Decorative background lines
    for x in range(0, WIDTH, 60):

        draw.line(
            [(x, 0), (x + 100, 280)],
            fill="#101b2b",
            width=1
        )

    # Red right section
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

    # FOREX
    draw.text(
        (390, 100),
        "FOREX",
        font=get_font(100, True),
        fill=WHITE
    )

    # NEWS
    draw.text(
        (750, 100),
        "NEWS",
        font=get_font(100, True),
        fill=RED
    )

    # Subtitle
    draw.text(
        (470, 220),
        "STAY AHEAD. TRADE SMART.",
        font=get_font(28),
        fill=GRAY
    )

    # ==========================================
    # MAIN NEWS CARD
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

    # Forex News text
    draw.text(
        (510, 350),
        "FOREX NEWS",
        font=get_font(45, True),
        fill=RED
    )

    # Current date
    current_date = datetime.now().strftime(
        "%b %d, %Y"
    )

    draw.text(
        (1000, 360),
        current_date,
        font=get_font(25),
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
        (130, 455),
        str(country).upper(),
        font=get_font(45, True),
        fill=WHITE
    )

    draw.text(
        (
