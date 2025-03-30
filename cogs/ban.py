"""
Ban Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

THIS FILE MIGHT FAIL THE FIRST TIME THE BOT IS RAN DEPENDING ON
IF banned.json EXISTS IN THE SAME DIRECTORY AS THE main.py
"""

import os
import discord
from discord import app_commands
from discord.ext import commands
from logging_config import create_new_logger

logger = create_new_logger(__name__)


class Ban(commands.Cog):
    """
    banned words list management commands
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Runs when the cog is loaded
        """
        logger.info("%s ready", self.__cog_name__)

    @commands.Cog.listener()
    async def on_message(self, message):
        """On user message event listener"""

        msg = str(message.content.lower())
        # Ignore messages that start with the bot's prefix
        if msg.startswith(f"{os.getenv('PREFIX')}"):
            return

    @app_commands.command(
        name="ban_word",
        description="Ban a word or phrase from being used in the server",
    )
    async def ban_word(self, interaction: discord.Interaction, word: str):
        """
        Ban a word or phrase from being used in the server
        """
        await interaction.response.send_message(
            f"Word '{word}' has been banned", ephemeral=True
        )


async def setup(bot):
    """
    Add the Ban cog to the bot
    """
    await bot.add_cog(Ban(bot), guilds=[discord.Object(id=842545435050508328)])
