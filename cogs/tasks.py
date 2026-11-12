"""
Tasks Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

Setup tasks to run periodically in your server.
"""

import os
import random
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands, tasks

from cogs.youtube import (
    RATEMYTAKEAWAY_YOUTUBE_CHANNEL_ID,
    query_latest_youtube_video_from_channel_id,
)
from utils.gif_search import search_gif
from utils.logging_config import create_new_logger

logger = create_new_logger(__name__)

EASTERN = ZoneInfo("America/New_York")

# Caturday posts every Saturday at 9 AM Eastern in this channel
CATURDAY_CHANNEL_ID = os.getenv("CATURDAY_CHANNEL_ID")
CATURDAY_POST_TIME = time(hour=9, tzinfo=EASTERN)
SATURDAY = 5  # datetime.weekday() value for Saturday
CATURDAY_GIF_QUERY = "caturday"
CATURDAY_PROCLAMATIONS = [
    "Happy Cat-urday my fellow Americans!",
    "I am pleased to announce that today is Cat-urday!",
    "My fellow Americans, by the power vested in me, I hereby declare today Cat-urday.",
    "Let me be clear, today is Cat-urday.",
    "Yes we can. And yes, it's Cat-urday.",
    "The state of our union is strong, and today it is Cat-urday.",
    "After careful deliberation with my cabinet, I can confirm today is Cat-urday.",
    "Folks, the cats have spoken. Happy Cat-urday!",
]


class Tasks(commands.Cog):
    """
    Tasks that loop perdiodically.
    """

    def __init__(self, bot):
        self.bot = bot
        self.running_tasks = {}
        self.previous_video_url = None

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Runs when the cog is loaded
        """
        logger.info("%s ready", self.__cog_name__)

    async def cog_load(self) -> None:
        """
        Start the tasks that run on their own when the cog is loaded
        """
        if CATURDAY_CHANNEL_ID:
            self.caturday_task.start()
        else:
            logger.info("CATURDAY_CHANNEL_ID not set, caturday task not started")

    async def cog_unload(self) -> None:
        """
        Stop the automatic tasks when the cog is unloaded
        """
        self.caturday_task.cancel()

    @commands.command(aliases=["start task", "run task", "start", "run"])
    @commands.has_permissions(administrator=True)
    async def start_task(
        self, ctx: commands.Context, task_name: str, channel_id: int = None
    ) -> None:
        """
        Start a task in a specific channel or the channel the command was run in by default.
        """
        # Check if the task exists and is an instance of tasks.Loop
        task = getattr(self, task_name, None)
        if task is None or not isinstance(task, tasks.Loop):
            await ctx.send(f"No task found with the name {task_name}.")
            logger.info("No task found with the name %s", task_name)
            return

        # Check if the task is already running
        if task.is_running():
            await ctx.send(f"The task {task_name} is already running.")
            logger.info("Task %s is already running", task_name)
            return

        # Get the channel to send messages to from the channel ID. If no channel ID is provided, use the channel the command was run in.
        channel = self.bot.get_channel(channel_id) if channel_id else ctx.channel

        # If channel is None, the channel ID provided is invalid or the bot does not have access to the channel. Send an error message and return.
        if channel is None:
            await ctx.send(f"Could not find channel with ID {channel_id}.")
            logger.info("Could not find channel with ID %s", channel_id)
            return

        # Store the task and channel ID in the running_tasks dictionary
        self.running_tasks[task_name] = {"task": task, "channel": channel}

        # Start the task. This is the last thing done because it will also run the task, so we wait until the end to start it.
        try:
            task.start()
        except Exception as e:
            await ctx.send(f"ERROR {e}")
            logger.error("Error starting task %s: %s", task_name, e)

        # Send a message to the channel where the start task command was ran from
        await ctx.send(f"The task {task_name} has been started.")
        logger.info(
            "Task %s started by user %s in channel %s",
            task_name,
            ctx.author.name,
            channel,
        )

    @commands.command(aliases=["stop task", "end task", "stop", "end"])
    @commands.has_permissions(administrator=True)
    async def stop_task(self, ctx: commands.Context, task_name: str) -> None:
        """
        Stop a task with the given name.
        """
        task_info = self.running_tasks.get(task_name)
        if task_info is None:
            await ctx.send(f"Task '{task_name}' is not running.")
            return

        try:
            task = task_info["task"]
            task.cancel()
            del self.running_tasks[task_name]
            await ctx.send(f"Task '{task_name}' stopped")
            logger.info("Task %s stopped by %s", task_name, ctx.author.id)
        except Exception as e:
            await ctx.send(f"ERROR {e}")
            logger.error("Error stopping task %s: %s", task_name, e)

    @commands.command(aliases=["tasks", "status"])
    async def show_tasks_status(self, ctx):
        """
        Show the status and details of all tasks.
        """
        # Check if there are any tasks running
        if not self.running_tasks:
            await ctx.send("No tasks have been started yet.")
            return

        # Iterate through all the tasks and send a message with the status of each task
        for task_name, task_info in self.running_tasks.items():
            task = task_info["task"]
            task_channel = task_info["channel"]
            status = "running" if task.is_running() else "stopped"

            channel_info = (
                f" (in channel <#{task_channel.id}>)" if task_channel.id else ""
            )

            next_iteration = task_info.get("task").next_iteration
            if next_iteration is not None:
                adjusted_next_iteration = next_iteration - timedelta(hours=4)
                next_iteration_info = (
                    ", next run at "
                    + adjusted_next_iteration.strftime("%m-%d-%y %H:%M:%S")
                )
            else:
                next_iteration_info = ""

            await ctx.send(
                f"Task '{task_name}' is {status}{channel_info}{next_iteration_info}"
            )

    @tasks.loop(hours=1)
    async def ratemytakeaway_task(self) -> None:
        """
        Task to fetch the latest video from Rate My Takeaway's channel
        """
        # Check if the current time is 2 PM EST (6 PM UTC) to run the task
        now = datetime.now()
        if now.hour == 13:
            # Get the channel to send the message to
            rmt_channel_info = self.running_tasks.get("ratemytakeaway_task")
            rmt_channel = rmt_channel_info["channel"]

            if rmt_channel is None:
                logger.error(
                    "No channel associated with ratemytakeaway_task, but task is running."
                )
                return

            # Fetch the latest video from Rate My Takeaway's channel
            latest_video = query_latest_youtube_video_from_channel_id(
                RATEMYTAKEAWAY_YOUTUBE_CHANNEL_ID
            )

            if latest_video is None:
                return

            # Check if the latest video is different from the previous one
            if latest_video["video_url"] != self.previous_video_url:
                await rmt_channel.send(
                    f"{latest_video['title']} - {latest_video['video_url']}"
                )
                self.previous_video_url = latest_video["video_url"]

                logger.info(
                    "Fetched the latest video from Rate My Takeaway's channel - %s",
                    latest_video["video_url"],
                )
            else:
                logger.info(
                    "Previous video url is the same as the latest video url - %s",
                    latest_video["video_url"],
                )

    @tasks.loop(time=CATURDAY_POST_TIME)
    async def caturday_task(self) -> None:
        """
        Task to post a caturday GIF and proclamation every Saturday.
        The loop runs every day at the post time and skips the days that aren't Saturday.
        """
        if datetime.now(EASTERN).weekday() != SATURDAY:
            return

        task_info = self.running_tasks.get("caturday_task")
        if task_info is None:
            logger.error(
                "No channel associated with caturday_task, but task is running."
            )
            return

        proclamation = random.choice(CATURDAY_PROCLAMATIONS)
        gif_url = await search_gif(CATURDAY_GIF_QUERY)
        message = f"{proclamation}\n{gif_url}" if gif_url else proclamation

        try:
            await task_info["channel"].send(message)
            logger.info("Caturday posted in channel %s", task_info["channel"])
        except discord.DiscordException:
            logger.exception(
                "Failed to post caturday in channel %s", task_info["channel"]
            )

    @caturday_task.before_loop
    async def before_caturday_task(self) -> None:
        """
        Wait for the bot to connect, then find the caturday channel.
        Skipped when the task was started with the start command, which sets the channel.
        """
        await self.bot.wait_until_ready()

        if "caturday_task" in self.running_tasks:
            return

        channel = self.bot.get_channel(int(CATURDAY_CHANNEL_ID))
        if channel is None:
            logger.error(
                "Could not find caturday channel with ID %s", CATURDAY_CHANNEL_ID
            )
            return

        self.running_tasks["caturday_task"] = {
            "task": self.caturday_task,
            "channel": channel,
        }
        logger.info("Caturday task scheduled in channel %s", channel)


async def setup(bot):
    """
    Add the cog to the bot
    """
    await bot.add_cog(Tasks(bot))
