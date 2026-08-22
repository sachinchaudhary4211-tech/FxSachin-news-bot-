import os
import discord
from discord.ext import commands

# ==========================================
# BOT SETTINGS
# ==========================================

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

ROLE_ID = 1540694379767795895

# ==========================================
# BOT SETUP
# ==========================================

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# ==========================================
# ROLE BUTTON
# ==========================================

class RoleButton(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Get Role",
        style=discord.ButtonStyle.green,
        custom_id="get_role_button"
    )
    async def get_role(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        role = interaction.guild.get_role(ROLE_ID)

        if role is None:
            await interaction.response.send_message(
                "❌ Role not found. Check your ROLE_ID.",
                ephemeral=True
            )
            return

        if role in interaction.user.roles:

            await interaction.user.remove_roles(role)

            await interaction.response.send_message(
                f"❌ {role.name} role removed.",
                ephemeral=True
            )

        else:

            await interaction.user.add_roles(role)

            await interaction.response.send_message(
                f"✅ You received the {role.name} role!",
                ephemeral=True
            )


# ==========================================
# BOT READY
# ==========================================

@bot.event
async def on_ready():

    bot.add_view(RoleButton())

    print("================================")
    print(f"Logged in as: {bot.user}")
    print(f"Bot ID: {bot.user.id}")
    print("Role button is ready!")
    print("================================")


# ==========================================
# START BOT
# ==========================================

if TOKEN is None:
    print("ERROR: DISCORD_BOT_TOKEN is not set!")
else:
    bot.run(TOKEN)
