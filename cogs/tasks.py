"""
Tasks Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

Setup tasks to run periodically in your server.
"""

import datetime
from discord.ext import commands, tasks

wednesday = 1  # Wednesday is 2 in Python's Datetime module
nine_am = datetime.time(hour=20, minute=40)


class Tasks(commands.Cog):
    """
    Tasks that loop perdiodically.
    """

    def __init__(self, bot):
        self.bot = bot
        self.tasks = []

    @commands.Cog.listener()
    async def on_ready(self):
        """
        runs when Cog is loaded and ready to use
        """
        print(f'{self} ready')

    @tasks.loop(seconds=20, minutes=0, hours=0)
    async def send_meme(self, channel):
        """
        Send the Wednesday meme on, you guessed it, Wednesday.
        """
        await channel.send(f"This is a meme")

    @commands.command()
    async def start_memes(self, ctx, seconds: int = 20, minutes: int = 0, hours: int = 0):
        """
        Start the Wednesday Meme Task. !start_memes (seconds) (minutes) (hours)
        """
        self.memes_channel = ctx.channel
        if seconds <= 1 or minutes < 0 or hours < 0:
            if seconds < 1:
                await ctx.send("```Seconds cannot be less than or equal to 1```")
            else:
                await ctx.send("```Minutes and hours cannot be less than 0```")
            return
        else:
            try:
                self.send_meme.change_interval(
                    seconds=seconds, minutes=minutes, hours=hours)
                self.send_meme.start(ctx.channel)
                self.tasks.append("Memes.task")
                await ctx.send(
                    f"```Memes task was started in this channel and will run every {self.send_meme.seconds} seconds, {self.send_meme.minutes} minutes, and {self.send_meme.hours} hours.```")
            except Exception as e:
                await ctx.send(f"```ERROR {e}```")

    @commands.command()
    async def stop_memes(self, ctx):
        """
        Stop the Wednesday Meme Task
        """
        if ctx.channel == self.memes_channel:
            try:
                self.send_meme.cancel()
                self.tasks.remove("Memes.task")
                await ctx.send("```Memes task was stopped in this channel.```")
            except Exception as e:
                print(f"ERROR {e}")
                await ctx.send(f"```ERROR {e}```")
        else:
            await ctx.send("```Task was not stopped.\nMust send the stop_memes command from the same channel the task is running in. You can check the status of tasks using the tasks_status command.```")

    @commands.command(aliases=['tasks', 'status'])
    async def tasks_status(self, ctx):
        """
        Show the status of all currently running tasks.
        """
        running_tasks = 'Running Tasks:\n'
        for task in self.tasks:
            if task == "Memes.task":
                task += " in Channel: " + str(self.memes_channel)
            running_tasks += task

        if self.tasks:
            message = running_tasks
        else:
            message = "There are no running tasks."

        await ctx.send(f"```{message}```")

    # async def wednesday_meme(self, ctx):
    #     now = datetime.datetime.now()
    #     today = datetime.date.today()
    #     days_until_wednesday = (wednesday - today.weekday()) % 7
    #     next_wednesday = today + datetime.timedelta(days=days_until_wednesday)
    #     next_wednesday_nine_am = datetime.datetime.combine(
    #         next_wednesday, nine_am)
    #     if now >= next_wednesday_nine_am:
    #         next_wednesday += datetime.timedelta(days=7)
    #         next_wednesday_nine_am = datetime.datetime.combine(
    #             next_wednesday, nine_am)
    #     seconds_until_nine_am = (next_wednesday_nine_am - now).seconds

    #     print("now", now)
    #     print("today", today)
    #     print("days_until_wednesday", days_until_wednesday)
    #     print("next_wednesday", next_wednesday)
    #     print("next_wednesday_nine_am", next_wednesday_nine_am)

    #     await asyncio.sleep(seconds_until_nine_am)


async def setup(bot):
    await bot.add_cog(Tasks(bot))
