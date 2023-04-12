"""
Tasks Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

Setup tasks to run periodically in your server.
"""

from datetime import datetime, timedelta
import asyncio
import pytz
import discord
from discord.ext import commands, tasks


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

    @commands.command(aliases=['tasks', 'status'])
    async def tasks_status(self, ctx):
        """
        Show the status of all currently running tasks.
        """
        running_tasks = 'Running Tasks:\n'
        for task in self.tasks:
            running_tasks += f'{task}\n'

        if self.tasks:
            message = running_tasks
        else:
            message = "There are no running tasks."

        await ctx.send(f'{message}')

    @tasks.loop(seconds=0, minutes=1, hours=0)
    async def custom_task(self, channel, content):
        await channel.send(f'{content}')

    @commands.command(aliases=['cct'])
    async def create_custom_task(self, ctx):
        """
        Start a new custom task with customizable time interval
        """
        # a check to ensure the prompts aren't interrupted by other user's / bot's messages
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        # prompt the user for a task name and if it already exists prompt again
        while True:
            try:
                await ctx.send("```Name the task, must be one word. Type 'cancel' to stop task creation```")
                task_name = await self.bot.wait_for('message', timeout=10.0, check=check)
                task_name = task_name.content.strip()
                # if the user enters 'cancel' then the command will stop
                if task_name == 'cancel':
                    await ctx.send('```Canceled task creation```')
                    return
                # Check if the task name already exists
                if task_name.lower() in [task.lower() for task in self.tasks]:
                    await ctx.send("```A task with this name already exists. Please choose a different name. Use !tasks to see the list of currently running tasks.```")
                else:
                    break
            except asyncio.TimeoutError:
                await ctx.send("```Task creation timed out.```")
                return

        # prompt the user for the content of their custom task
        try:
            await ctx.send("What should be sent to the channel when the task runs?")
            task_content = await self.bot.wait_for('message', timeout=10.0, check=check)
            task_content = task_content.content
        except asyncio.TimeoutError:
            await ctx.send("```Task creation timed out.```")
            return

        # prompt the user for the time interval their custom task will loop on
        await ctx.send("Enter the task interval in seconds, minutes, and hours (separated by spaces).\n\
                       (seconds > 1) (minutes >= 0) (hours >= 0)")
        try:
            response = await self.bot.wait_for('message', timeout=60.0, check=check)
            interval_time = response.content.strip().split()
            if len(interval_time) == 1:
                seconds = int(interval_time[0])
                minutes = 0
                hours = 0
            elif len(interval_time) == 2:
                seconds = int(interval_time[0])
                minutes = int(interval_time[1])
                hours = 0
            elif len(interval_time) >= 3:
                seconds = int(interval_time[0])
                minutes = int(interval_time[1])
                hours = int(interval_time[2])
            if seconds <= 1 or minutes < 0 or hours < 0:
                raise ValueError("Invalid time interval.")
            else:
                self.custom_task.change_interval(
                    seconds=seconds, minutes=minutes, hours=hours)
                self.custom_task.start(ctx.channel, task_content)
                self.tasks.append(task_name)
                await ctx.send(
                    f"```A new task '{task_name}' was started in this channel and will run every {seconds} seconds, {minutes} minutes, and {hours} hours.```")
        except Exception as e:
            await ctx.send(f"```ERROR {e}```")

    @commands.command(aliases=['stop'])
    async def stop_task(self, ctx, task_name):
        """
        Stops a task by its task_name
        """
        try:
            for task in self.tasks:
                print(self.tasks)
                print(task, task_name)
                if task == task_name:
                    # Stop the task and remove it from the task list
                    task_to_stop = self.custom_task
                    task_to_stop.cancel()
                    self.tasks.remove(task_name)
                    await ctx.send(f"```Task '{task_name}' was stopped in this channel.```")
                    return
            await ctx.send(f"```Task '{task_name}' is not currently running in this channel.```")
        except Exception as e:
            print(f"ERROR {e}")
            await ctx.send(f"```ERROR {e}```")
        else:
            await ctx.send("```Task was not stopped.\nMust send the stop_task command from the same channel the task is running in. You can check the status of tasks using the tasks_status command.```")

    @commands.command(aliases=['twm'])
    async def toggle_wednesday_meme(self, ctx):
        """
        Toggle the Wednesday meme task
        """
        if self.wednesday_meme.is_running():
            self.wednesday_meme.cancel()
            self.tasks.remove('wednesday')
            await ctx.send(f"```Wednesday meme task stopped in {ctx.channel}.```")
        else:
            self.wednesday_meme.start(ctx.channel)
            self.tasks.append('wednesday')
            await ctx.send(f"```Wednesday meme task started in {ctx.channel}.```")

    @tasks.loop(hours=1)
    async def wednesday_meme(self, channel):
        # Check if today is Wednesday and the current time is 9:00am EST
        now = datetime.now(pytz.timezone('US/Eastern'))

        not_sent = True
        if now.weekday() == 2 and now.hour == 9:
            while (not_sent):
                # Replace with your channel ID
                await channel.send(file=discord.File('gifs/memes/wednesday.jpg'))
                not_sent = False
            not_sent = True


async def setup(bot):
    await bot.add_cog(Tasks(bot))
