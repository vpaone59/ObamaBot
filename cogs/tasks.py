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
        self.send_wed_meme.start()

    @commands.Cog.listener()
    async def on_ready(self):
        """
        runs when Cog is loaded and ready to use
        """
        print(f'{self} ready')

    @tasks.loop(count=1)
    async def send_wed_meme(self):
        print(f"{self.command.name} started on channel")
        now = datetime.datetime.now()
        if now.weekday() == wednesday and now.time() == nine_am:
            send_to_channel = self.bot.get_channel()

            await send_to_channel.send(file=discord.File('gifs/obama/wednesday.jpg'))

    @send_wed_meme.before_loop
    async def before_send_hi(self):
        # Calculate the time until the next Wednesday at 9:00am
        now = datetime.datetime.now()
        next_wednesday = now + \
            datetime.timedelta((wednesday - now.weekday()) % 7)
        time_until_next_wednesday = datetime.datetime.combine(
            next_wednesday, nine_am) - now

        # Wait until it's time to send the first "Hi" message
        await discord.utils.sleep_until(now + time_until_next_wednesday)


async def setup(bot):
    await bot.add_cog(Tasks(bot))
