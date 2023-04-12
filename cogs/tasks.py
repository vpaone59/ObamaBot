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

    @commands.command(aliases=['tct'])
    async def toggle_custom_task(self, ctx):
        """
        Toggle the Wednesday meme task
        """
        if self.wednesday_meme.is_running():
            self.wednesday_meme.cancel()
            self.tasks.remove(self.wednesday_meme)
            print(self.tasks)
            await ctx.send("```Wednesday meme task stopped.```")
        else:
            print('start')
            self.wednesday_meme.start()
            self.tasks.append(self.wednesday_meme)
            print(self.tasks)
            await ctx.send("```Wednesday meme task started.```")

    @commands.command(aliases=['start'])
    async def start_custom_task(self, ctx):
        """
        Start a new custom task !start_custom_task
        """
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        if self.toggle_custom_task.is_running():
            self.toggle_custom_task.cancel()
            self.tasks.remove(self.toggle_custom_task)

        await ctx.send("What would you like to name this task?")
        try:
            task_name = await self.bot.wait_for('message', timeout=10.0, check=lambda message: message.author == ctx.author)
            task_name = task_name.content.strip()
        except asyncio.TimeoutError:
            await ctx.send("```Task creation timed out.```")
            return

        # Check if the task name already exists
        for task in self.tasks:
            if task['name'] == task_name:
                await ctx.send("```A task with this name already exists. Please choose a different name.```")
                return

        await ctx.send("What should be sent to the channel when the task runs?")
        try:
            task_content = await self.bot.wait_for('message', timeout=20.0, check=check)
            task_content = task_content.content
        except asyncio.TimeoutError:
            await ctx.send("```Task creation timed out.```")
            return

        await ctx.send("Enter the task interval in seconds, minutes, and hours (separated by spaces):")
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
                # Start the task
                self.start_task(new_task)
                # Add the task to the list of running tasks
                print(new_task, "new_task")
                self.tasks.append(new_task)
                print("TASK LIST", self.tasks)

                await ctx.send(
                    f"```A new task '{task_name}' was started in this channel and will run every {new_task['interval']['seconds']} seconds, {new_task['interval']['minutes']} minutes, and {new_task['interval']['hours']} hours.```")
        except asyncio.TimeoutError:
            await ctx.send("```Task creation timed out.```")
        except ValueError:
            await ctx.send("```Invalid time interval.```")
        except Exception as e:
            await ctx.send(f"```ERROR {e}```")

    @commands.command(aliases=['stop'])
    async def stop_task(self, ctx, task_name):
        """
        Stops a task by its task_name
        """
        try:
            for task in self.tasks:
                if task == task_name:
                    # Stop the task and remove it from the task list
                    self.send_task.cancel()
                    self.tasks.remove(task_name)
                    await ctx.send(f"```Task '{task_name}' was stopped in this channel.```")
                    return
            await ctx.send(f"```Task '{task_name}' is not currently running in this channel.```")
        except Exception as e:
            print(f"ERROR {e}")
            await ctx.send(f"```ERROR {e}```")
        else:
            await ctx.send("```Task was not stopped.\nMust send the stop_task command from the same channel the task is running in. You can check the status of tasks using the tasks_status command.```")

    @commands.command(aliases=['tasks', 'status'])
    async def tasks_status(self, ctx):
        """
        Show the status of all currently running tasks.
        """
        print("TASKS")
        running_tasks = 'Running Tasks:\n'
        for task in self.tasks:
            running_tasks += task

        if self.tasks:
            message = running_tasks
        else:
            message = "There are no running tasks."

        await ctx.send(f"```{message}```")

    @commands.command(aliases=['twm'])
    async def toggle_wednesday_meme(self, ctx):
        """
        Toggle the Wednesday meme task
        """
        if self.wednesday_meme.is_running():
            self.wednesday_meme.cancel()
            self.tasks.remove(self.wednesday_meme)
            print(self.tasks)
            await ctx.send(f"```Wednesday meme task stopped in {ctx.channel}.```")
        else:
            print('start')
            self.wednesday_meme.start(ctx.channel)
            self.tasks.append(self.wednesday_meme)
            print(self.tasks)
            await ctx.send(f"```Wednesday meme task started in {ctx.channel}.```")

    @tasks.loop(hours=1)
    async def wednesday_meme(self, channel):
        # Check if today is Wednesday and the current time is 9:00am EST
        now = datetime.now(pytz.timezone('US/Eastern'))
        print(now)
        not_sent = True
        if now.weekday() == 2 and now.hour == 9:
            while (not_sent):
                # Replace with your channel ID
                await channel.send(file=discord.File('gifs/memes/wednesday.jpg'))
                not_sent = False
            not_sent = True
        else:
            print("not wednesday")


async def setup(bot):
    await bot.add_cog(Tasks(bot))
