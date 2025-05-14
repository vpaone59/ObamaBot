"""
General Commands Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

These are general use commands that any bot should have by default.
"""

import discord
from discord.ext import commands
from logging_config import create_new_logger

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
    async def hello(self, ctx):
        """
        Reply mention to the user
        """
        try:
            await ctx.channel.send(f"Hello {ctx.author.mention}!")
        except Exception as e:
            logger.error(f"USER: {ctx.message.author} ERROR: {e}")
            await ctx.channel.send(f"Error {__name__}: {e}")

    @commands.command(name="hiall")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def hello_everyone(self, ctx):
        """
        Reply mention to all users
        """
        try:
            await ctx.send(f"Hello {ctx.message.guild.default_role}!")
        except Exception as e:
            logger.error(f"USER: {ctx.message.author} ERROR: {e}")
            await ctx.channel.send(f"Error {__name__}: {e}")

    @commands.command(name="ping", aliases=["p"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def ping(self, ctx):
        """
        Send ping to server
        """
        try:
            bot_latency = round(self.bot.latency * 1000, 2)
            await ctx.send(f"pong {bot_latency}ms")
        except Exception as e:
            logger.error(f"USER: {ctx.message.author} ERROR: {e}")
            await ctx.channel.send(f"Error {__name__}: {e}")

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

    @commands.command(aliases=["gn"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def goodnight(self, ctx):
        """
        Reply with media
        """
        await ctx.send(
            "Goodnight and God Bless!",
            file=discord.File("gifs/obama/obama-sleep.jpeg"),
        )

    @commands.command(name="fibonacci", aliases=["fib"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def fib(self, ctx, num):
        """
        Calculate fibonacci of the parameter input
        paramter num: number in the fibonacci sequence to calculate
        """
        try:
            n = int(num)
            result = fibonacci(n)
            await ctx.send(f"```Result:\nFibonnaci of {num} = {result}```")

        except Exception as e:
            logger.error(f"USER: {ctx.message.author} ERROR: {e}")
            await ctx.channel.send(f"Error {__name__}: {e}")

    @commands.command(name="current_guilds", aliases=["guilds", "servers"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def current_guilds(self, ctx):
        """
        Return the number of guilds(servers) this bot is currently in
        """
        try:
            await ctx.channel.send("I'm in " + str(len(self.bot.guilds)) + " servers!")
        except Exception as e:
            logger.error(f"USER: {ctx.message.author} ERROR: {e}")
            await ctx.channel.send(f"Error {__name__}: {e}")


def fibonacci(n):
    """
    calculate fibonacci sequence for a given n
    """
    if n < 0:
        return "Invalid input"
    elif n == 0:
        return 0
    elif n == 1 or n == 2:
        return 1
    else:
        fib = fibonacci(n - 1) + fibonacci(n - 2)
        return fib


async def setup(bot):
    await bot.add_cog(General(bot))
