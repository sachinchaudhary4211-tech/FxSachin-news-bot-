import os
import requests
from io import BytesIO
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont


# Get webhook URL from GitHub Secret
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


def get_font(size, bold=False):
    if bold:
        path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    else:
        path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    return ImageFont.truetype(path, size)


def draw_text(draw, position, text, font, fill):
    draw.text(position, text, font=font, fill=fill)


def create_news_image(country, event, time_value,
                      forecast, previous, impact):

    WIDTH = 1400
    HEIGHT = 900

    image = Image.new("RGB", (WIDTH, HEIGHT), "#0b1019")
    draw = ImageDraw.Draw(image)

    WHITE = "#f2f4f8"
    GRAY = "#9da7b8"
    RED = "#ff3131"
    BLUE = "#3d8cff"
    GREEN = "#55c74d"
    DARK = "#111927"
    BORDER = "#2a3445"

    # HEADER
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

    for i, height in enumerate([70, 120, 50, 150, 90, 180]):
        x = candle_x + (i * 50)
        y = 230 - height

        draw.line(
            [(x + 12, y - 20), (x + 12, y + height + 20)],
            fill=RED,
            width=3
        )

        draw.rectangle(
            [(x, y), (x + 24, y + height)],
            fill=RED
        )

    # Logo
    draw_text(
        draw,
        (590, 50),
        "FXSACHIN",
        get_font(38, True),
        WHITE
    )

    # Title
    draw_text(
        draw,
        (390, 100),
        "FOREX",
        get_font(100, True),
        WHITE
    )

    draw_text(
        draw,
        (750, 100),
        "NEWS",
        get_font(100, True),
        RED
    )

    draw_text(
        draw,
        (470, 220),
        "STAY AHEAD. TRADE SMART.",
        get_font(28),
        GRAY
    )

    # NEWS CARD
    card_top = 300

    draw.rounded_rectangle(
        [(40, card_top), (1360, 850)],
        radius=30,
        fill=DARK,
        outline=BORDER,
        width=3
    )

    # Impact color
    impact_color = RED

    if impact.lower() == "medium":
        impact_color = "#ffb020"
    elif impact.lower() == "low":
        impact_color = GREEN

    draw.ellipse(
        [(80, 350), (130, 400)],
        fill=impact_color
    )

    draw_text(
        draw,
        (160, 350),
        f"{impact.upper()} IMPACT",
        get_font(45, True),
        WHITE
    )

    draw_text(
        draw,
        (510, 350),
        "FOREX NEWS",
        get_font(45, True),
        RED
    )

    current_date = datetime.now().strftime("%b %d, %Y")

    draw_text(
        draw,
        (1000, 360),
        current_date,
        get_font(25),
        GRAY
    )

    # COUNTRY
    draw.rounded_rectangle(
        [(80, 440), (1320, 550)],
        radius=20,
        fill="#0d1522",
        outline=BORDER,
        width=2
    )

    draw_text(
        draw,
        (130, 460),
        country
