"""
Custom1 Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

This Cog is custom made for a specific server and will not work in normal servers.
"""

import os
import random
import logging
import discord
from discord.ext import commands
from logging_config import setup_logging

logger = setup_logging(__name__)

FRIEND_GUILDS = os.getenv("FRIEND_GUILD_IDS")


class Friends(commands.Cog):
    """
    Custom commands made for specific guilds
    For friends :)
    """

    def __init__(self, bot):
        self.bot = bot
        self.ethan_enabled = False  # Flag for Ethan reactions
        self.walter_enabled = False  # Flag for Walter reactions
        self.inc_enabled = False  # Flag for INC functionality

    @commands.Cog.listener()
    async def on_ready(self):
        """
        runs when Cog is loaded and ready to use
        """
        print(f"{self} ready")

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        whenever a message is sent this Cog will listen and execute code below
        """
        string_message = str(message.content)

        # return whenever a prefix is detected without a command attached
        if string_message.startswith(f'{os.getenv("PREFIX")}'):
            return

        if str(message.guild.id) not in FRIEND_GUILDS:
            return

        # Ethan reactions (toggleable)
        if self.ethan_enabled and message.author.id == 166964846179385344:
            await message.add_reaction("♿")

        # Walter reactions (toggleable)
        if self.walter_enabled and message.author.id == 965414583860883456:
            walter_int = random.randint(1, 3)
            if walter_int == 1:
                await message.channel.send(
                    file=discord.File("gifs/weird/boner_alert.jpg")
                )

        # if message.guild.id == 842545435050508328:
        #     if string_message.startswith("INC"):
        #         format_link = format_incident_link(string_message)
        #         await message.channel.send(f"{format_link}")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def toggle_ethan(self, ctx):
        """
        Toggle reactions for Ethan's messages.
        """
        self.ethan_enabled = not self.ethan_enabled
        if self.ethan_enabled:
            await ctx.send("Ethan reactions enabled!")
        else:
            await ctx.send("Ethan reactions disabled.")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def toggle_walter(self, ctx):
        """
        Toggle reactions for Walter's messages.
        """
        self.walter_enabled = not self.walter_enabled
        if self.walter_enabled:
            await ctx.send("Walter reactions enabled!")
        else:
            await ctx.send("Walter reactions disabled.")


def format_incident_link(incident_number):
    """
    Format incident number to a clickable link
    """
    return f"https://s.rowan.edu/{incident_number}"


async def setup(bot):
    await bot.add_cog(Friends(bot))
