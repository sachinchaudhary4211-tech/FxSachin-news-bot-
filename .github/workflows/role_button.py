import discord
from discord.ext import commands

# ==========================================
# SETTINGS
# ==========================================

TOKEN = "1540679654275420241"

# NEWS ROLE ID
ROLE_ID = 1540675428572987452

# CHANNEL WHERE THE NEWS BANNER WILL APPEAR
CHANNEL_ID = 123456789012345678


# ==========================================
# BOT SETUP
# ==========================================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# ==========================================
# 📰 NEWS ROLE BUTTON
# ==========================================

class NewsRoleButton(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="📰 NEWS",
        style=discord.ButtonStyle.primary,
        custom_id="news_role_button"
    )
    async def news_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        role = interaction.guild.get_role(ROLE_ID)

        if role is None:
            await interaction.response.send_message(
                "❌ NEWS role not found!",
                ephemeral=True
            )
            return

        # If user already has NEWS role → remove it
        if role in interaction.user.roles:

            await interaction.user.remove_roles(
                role,
                reason="User removed NEWS role"
            )

            await interaction.response.send_message(
                "🔕 NEWS role removed successfully!",
                ephemeral=True
            )

        # If user doesn't have role → give it
        else:

            await interaction.user.add_roles(
                role,
                reason="User received NEWS role"
            )

            await interaction.response.send_message(
                "📰 You now have the NEWS role!",
                ephemeral=True
            )


# ==========================================
# SEND NEWS BANNER
# ==========================================

async def send_news_banner():

    channel = bot.get_channel(CHANNEL_ID)

    if channel is None:
        print("❌ Channel not found!")
        return

    embed = discord.Embed(
        title="📰 BREAKING NEWS • MARKET ALERTS",
        description=(
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📡 **STAY CONNECTED TO THE MARKETS**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"

            "Get important Forex and economic news "
            "directly in this server.\n\n"

            "🔴 **HIGH IMPACT NEWS**\n"
            "Important market-moving events.\n\n"

            "🟠 **MEDIUM IMPACT NEWS**\n"
            "Important economic updates and announcements.\n\n"

            "🟢 **LOW IMPACT NEWS**\n"
            "Stay updated with upcoming market events.\n\n"

            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "👇 **WANT TO RECEIVE NEWS ALERTS?**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"

            "**Click the 📰 NEWS button below to get the role!**"
        )
    )

    embed.set_footer(
        text="🔔 Stay informed • Stay prepared • Stay ahead"
    )

    await channel.send(
        embed=embed,
        view=NewsRoleButton()
    )

    print("📰 NEWS banner sent!")


# ==========================================
# BOT READY
# ==========================================

@bot.event
async def on_ready():

    # Register persistent button
    bot.add_view(NewsRoleButton())

    print(f"✅ Logged in as {bot.user}")
    print("📰 NEWS role system is ready!")

    # Send banner once when bot starts
    await send_news_banner()


# ==========================================
# RUN BOT
# ==========================================

bot.run(TOKEN)
