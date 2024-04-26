"""
Media Cog for ObamaBot by Vincent Paone https://github.com/vpaone59
"""

import discord
from discord.ext import commands


class Media(commands.Cog):
    """
    Media cogs/commands for Obama Bot
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        runs when Cog is loaded and ready to use
        """
        print(f"{self} ready")

    @commands.Cog.listener("on_message")
    async def obama_message(self, message):
        """
        Whenever a message is sent in any channel and guild
        """
        # this is to prevent the bot from replying to itself
        if message.author == self.bot.user or message.author.bot:
            return

    @commands.command(aliases=["monkey", "m", "gorilla"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def monkey_falling(self, ctx):
        """
        Reply with media
        """
        await ctx.send(file=discord.File("media/monkey-fall.gif"))

    @commands.command(aliases=["thanks"])
    async def thanks_obama(self, ctx):
        """
        Reply with media
        """
        await ctx.channel.send(
            "You're welcome! <:obamacare:844291609663111208>\n",
            file=discord.File("media/obama-smile.jpg"),
        )

    @commands.command(aliases=["joe", "biden", "brandon", "jack"])
    async def joe_biden(self, ctx):
        """
        Reply with media
        """
        await ctx.channel.send(file=discord.File("media/biden-smile.png"))


async def setup(bot):
    await bot.add_cog(Media(bot))
