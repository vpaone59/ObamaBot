"""
Custom1 Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

This Cog is custom made for a specific server and will not work in normal servers.
"""

import os
import random
import logging
import discord
from discord.ext import commands

logger = logging.getLogger(__name__)

BEE_REACTS = [
    "<:obamagiga:844300314936213565> :point_right: :bee:",
    ":bee: :broom: <:feelsobama:842634906999193620>",
    "<:obamajoy:842822700912476190> :fire: :bee: :fire:",
]
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
        self.dj_enabled = False  # Flag for DJ functionality
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

        # # if DJ (ID= 123107464240562180) is @ mentioned
        # for user in message.mentions:
        #     if user.id == 123107464240562180:
        #         file_name = get_random_batman_deej_file()
        #         if file_name:
        #             file_path = os.path.join("gifs/memes", file_name)
        #             await message.channel.send(file=discord.File(file_path))
        #         break  # Once the user is found, we can break out of the loop

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

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def toggle_dj(self, ctx):
        """
        Toggle the DJ functionality on or off.
        """
        self.dj_enabled = not self.dj_enabled
        if self.dj_enabled:
            await ctx.send("DJ functionality enabled. Mention me to play memes!")
        else:
            await ctx.send("DJ functionality disabled.")

    @commands.command(aliases=["bee", "b"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def bees(self, ctx):
        """
        Random reaction for a bees command
        """
        try:
            await ctx.channel.send(random.choice(BEE_REACTS))
        except Exception as e:
            logger.error(f"USER: {ctx.message.author} ERROR: {e}")
            await ctx.channel.send(f"Error {__name__}: {e}")

    @commands.command(aliases=["reeve", "reevez", "reeves!"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def reeves(self, ctx):
        """
        Send a picture of Reeves!
        """
        try:
            await ctx.channel.send(file=discord.File("gifs/lads/reeves_gun_permit.png"))
        except Exception as e:
            logger.error(f"USER: {ctx.message.author} ERROR: {e}")
            await ctx.channel.send(f"Error {__name__}: {e}")

    @commands.command(aliases=["dumpydave"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def dumpy(self, ctx):
        """
        Send a picture of Dave's fat ass
        """
        try:
            await ctx.channel.send(file=discord.File("gifs/lads/dumpy_dave_2.png"))
        except Exception as e:
            logger.error(f"USER: {ctx.message.author} ERROR: {e}")
            await ctx.channel.send(f"Error {__name__}: {e}")


def format_incident_link(incident_number):
    """
    Format incident number to a clickable link
    """
    return f"https://s.rowan.edu/{incident_number}"


def get_random_batman_deej_file():
    """
    Get all files in the memes directory that are of .png and contain 'batman_deej' in the filename
    """
    folder_path = "gifs/memes"
    files = [
        file
        for file in os.listdir(folder_path)
        if file.endswith(".png") and "batman_deej" in file
    ]
    if files:
        return random.choice(files)
    else:
        return None


async def setup(bot):
    await bot.add_cog(Friends(bot))
