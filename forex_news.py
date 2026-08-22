WEBHOOK_URL = "https://discord.com/api/webhooks/1540641249135165490/0yIDqzxhUMMDbt2sW0MeY27gtNMo0QNOzisEbFtz_PS9p3G2hgA36zs5ZtsfnM6YEbpt"


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

    # Background
    image = Image.new("RGB", (WIDTH, HEIGHT), "#0b1019")
    draw = ImageDraw.Draw(image)

    # Colors
    WHITE = "#f2f4f8"
    GRAY = "#9da7b8"
    RED = "#ff3131"
    BLUE = "#3d8cff"
    GREEN = "#55c74d"
    DARK = "#111927"
    BORDER = "#2a3445"

    # ==============================
    # HEADER / BANNER
    # ==============================

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

    # Red area on right
    draw.rectangle(
        [(1050, 0), (WIDTH, 280)],
        fill="#21080d"
    )

    # Small candlestick-style decorations
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

    # Logo text
    draw_text(
        draw,
        (590, 50),
        "FXSACHIN",
        get_font(38, True),
        WHITE
    )

    # Main title
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
        get_font(28, False),
        GRAY
    )

    # ==============================
    # NEWS CARD
    # ==============================

    card_top = 300

    draw.rounded_rectangle(
        [(40, card_top), (1360, 850)],
        radius=30,
        fill=DARK,
        outline=BORDER,
        width=3
    )

    # Impact heading
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

    # Date
    current_date = datetime.now().strftime("%b %d, %Y")

    draw_text(
        draw,
        (1000, 360),
        current_date,
        get_font(25),
        GRAY
    )

    # ==============================
    # COUNTRY
    # ==============================

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
        country.upper(),
        get_font(45, True),
        WHITE
    )

    draw_text(
        draw,
        (130, 510),
        "COUNTRY / CURRENCY",
        get_font(18),
        GRAY
    )

    # ==============================
    # EVENT
    # ==============================

    draw.rounded_rectangle(
        [(80, 580), (1320, 690)],
        radius=20,
        fill="#0d1522",
        outline=BORDER,
        width=2
    )

    draw_text(
        draw,
        (130, 600),
        "EVENT",
        get_font(20, True),
        RED
    )

    # Limit long event text
    event_text = event[:45]

    draw_text(
        draw,
        (130, 635),
        event_text,
        get_font(40, True),
        WHITE
    )

    # ==============================
    # BOTTOM DETAILS
    # ==============================

    sections = [
        ("TIME", time_value, "#9b8cff"),
        ("FORECAST", forecast, GREEN),
        ("PREVIOUS", previous, BLUE),
        ("IMPACT", impact.upper(), impact_color)
    ]

    start_x = 100
    box_width = 300

    for i, (label, value, color) in enumerate(sections):

        x = start_x + (i * box_width)

        if i > 0:
            draw.line(
                [(x - 30, 720), (x - 30, 820)],
                fill=BORDER,
                width=2
            )

        draw_text(
            draw,
            (x, 720),
            label,
            get_font(22, True),
            color
        )

        draw_text(
            draw,
            (x, 760),
            str(value),
            get_font(38, True),
            WHITE if label != "IMPACT" else color
        )

    # Footer
    draw_text(
        draw,
        (550, 835),
        "FxSachin • Forex News",
        get_font(20),
        GRAY
    )

    # Convert image to memory
    image_bytes = BytesIO()

    image.save(
        image_bytes,
        format="PNG"
    )

    image_bytes.seek(0)

    return image_bytes


def send_to_discord(country, event, time_value,
                    forecast, previous, impact):

    image_file = create_news_image(
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
            image_file,
            "image/png"
        )
    }

    payload = {
        "content": "",
        "embeds": [
            {
                "image": {
                    "url": "attachment://forex_news.png"
                },
                "footer": {
                    "text": "FxSachin • Automated Forex News"
                }
            }
        ]
    }

    response = requests.post(
        WEBHOOK_URL,
        data={
            "payload_json": __import__("json").dumps(payload)
        },
        files=files
    )

    print("Discord Status:", response.status_code)
