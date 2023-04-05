"""
Custom1 Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

This Cog is custom made for a specific server and will not work in normal servers.
"""

import datetime
import discord
from discord.ext import commands, tasks

wednesday = 1  # Wednesday is 2 in Python's Datetime module
nine_am = datetime.time(hour=20, minute=40)


class Tasks(commands.Cog):
    """
    custom commands made for a specific discord guild
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        runs when Cog is loaded and ready to use
        """
        print(f'{self} ready')

    @tasks.loop(seconds=5, minutes=0, hours=0)
    async def send_wed_meme(self, channel):
        print(f"sending meme")
        await channel.send("meme")
        # await self.send(file=discord.File('gifs/obama/wednesday.jpg'))

    @commands.command()
    async def start_memes(self, ctx):
        print('starting')
        try:
            self.send_wed_meme.start(ctx.channel)
        except Exception as e:
            print(f'ERROR {e}')

    @commands.command()
    async def stop_memes(self, ctx):
        print('stopping')
        try:
            self.send_wed_meme.cancel()
        except Exception as e:
            print(f'ERROR {e}')


async def setup(bot):
    await bot.add_cog(Tasks(bot))
