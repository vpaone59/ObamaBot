"""
General Commands Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

These are general use commands that any bot should have by default.
"""

import discord
from discord.ext import commands

from utils.logging_config import create_new_logger

logger = create_new_logger(__name__)


class General(commands.Cog):
    """
    general commands for a Bot
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Runs when the cog is loaded
        """
        logger.info("%s ready", self.__cog_name__)

    @commands.command(aliases=["hey", "hi"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def hello(self, ctx: commands.Context):
        """
        Reply mention to the user
        """
        try:
            logger.info(
                "User %s (%s) used hello command in %s",
                ctx.author,
                ctx.author.id,
                ctx.guild,
            )
            await ctx.send(f"Hello {ctx.author.mention}!")
        except discord.DiscordException:
            logger.exception("Error in hello command for user %s", ctx.author)
            await ctx.send("Sorry, I couldn't send a greeting right now.")

    @commands.command(name="hiall")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def hello_everyone(self, ctx):
        """
        Reply mention to all users
        """
        try:
            await ctx.send(f"Hello {ctx.message.guild.default_role}!")
        except discord.DiscordException:
            logger.exception(
                "Failed to send greeting to all users for %s", ctx.message.author
            )
            await ctx.send("Sorry, I couldn't send that message.")

    @commands.command(name="ping", aliases=["p"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def ping(self, ctx):
        """
        Send ping to server
        """
        try:
            bot_latency = round(self.bot.latency * 1000, 2)
            await ctx.send(f"pong {bot_latency}ms")
        except discord.DiscordException:
            logger.exception(
                "Failed to send ping response for user %s", ctx.message.author
            )
            await ctx.send("Sorry, I couldn't send that message.")

    @commands.command(aliases=["gm"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def goodmorning(self, ctx):
        """
        Reply with media
        """
        await ctx.send(
            "Goodmorning my fellow Americans!",
            file=discord.File("gifs/obama/obama-smile.jpg"),
        )

    @commands.command(name="current_guilds", aliases=["guilds", "servers"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def current_guilds(self, ctx):
        """
        Return the number of guilds(servers) this bot is currently in
        """
        try:
            await ctx.send(f"I'm in {len(self.bot.guilds)} servers!")
        except discord.DiscordException:
            logger.exception(
                "Failed to send guild count for user %s", ctx.message.author
            )
            await ctx.send("Sorry, I couldn't send that message.")


async def setup(bot):
    await bot.add_cog(General(bot))
