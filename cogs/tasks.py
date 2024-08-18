"""
Tasks Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

Setup tasks to run periodically in your server.
"""

import os
from datetime import datetime, timedelta
from discord.ext import commands, tasks
from cogs.youtube import (
    RATEMYTAKEAWAY_YOUTUBE_CHANNEL_ID,
    query_latest_youtube_video_from_channel_id,
)
from logging_config import create_new_logger

logger = create_new_logger(__name__)
RMT_CHANNEL_ID = os.getenv("RMT_CHANNEL_ID")


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
        logger.info(f"{self} ready")

    @commands.command(aliases=["start task", "run task", "start", "run"])
    async def start_task(self, ctx, task_name: str, channel_id: int = None):
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
    async def stop_task(self, ctx, task_name: str):
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
    async def ratemytakeaway_task(self):
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


async def setup(bot):
    """
    Add the cog to the bot
    """
    await bot.add_cog(Tasks(bot))
