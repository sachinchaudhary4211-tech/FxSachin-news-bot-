import os
import discord
from discord.ext import commands


# ==========================================
# SETTINGS
# ==========================================

# Gets the bot token securely from GitHub Secrets
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Your NEWS role ID
ROLE_ID = 1540688570480730184

# Channel where the NEWS banner will be sent
CHANNEL_ID = 1537396245851807788


# ==========================================
# BOT SETUP
# ==========================================

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# ==========================================
# NEWS ROLE BUTTON
# ==========================================

class NewsRoleButton(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="NEWS",
        emoji="📰",
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
                "❌ NEWS role not found.",
                ephemeral=True
            )
            return

        if role in interaction.user.roles:

            await interaction.user.remove_roles(role)

            await interaction.response.send_message(
                "🔕 You have been removed from NEWS updates.",
                ephemeral=True
            )

        else:

            await interaction.user.add_roles(role)

            await interaction.response.send_message(
                "📰 You will now receive NEWS updates!",
                ephemeral=True
            )


# ==========================================
# BOT READY
# ==========================================

@bot.event
async def on_ready():

    print(f"Logged in as {bot.user}")

    bot.add_view(NewsRoleButton())

    channel = bot.get_channel(CHANNEL_ID)

    if channel is None:
        print("ERROR: Channel not found.")
        return

    print(f"Bot is ready in channel: {channel.name}")


# ==========================================
# COMMAND TO POST NEWS BANNER
# ==========================================

@bot.command()
@commands.has_permissions(administrator=True)
async def news(ctx):

    embed = discord.Embed(
        title="📰 FOREX NEWS UPDATES",
        description=(
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "**Stay updated with important Forex news.**\n\n"
            "Click the button below to receive\n"
            "**automatic NEWS notifications.**\n\n"
            "🔔 High Impact News\n"
            "📊 Low Impact News\n"
            "💵 USD Market Updates\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "**Your trade. Your decision. Your responsibility.**"
        )
    )

    await ctx.send(
        embed=embed,
        view=NewsRoleButton()
    )


# ==========================================
# START BOT
# ==========================================

if TOKEN is None:
    print("ERROR: DISCORD_BOT_TOKEN secret was not found.")
else:
    bot.run(TOKEN)
