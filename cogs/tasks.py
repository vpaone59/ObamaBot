"""
Tasks Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

Setup tasks to run periodically in your server.
"""

from datetime import datetime
from discord.ext import commands, tasks
from cogs.youtube import (
    RATEMYTAKEAWAY_YOUTUBE_CHANNEL_ID,
    query_latest_youtube_video_from_channel_id,
)
from logging_config import create_new_logger

logger = create_new_logger(__name__)


class Tasks(commands.Cog):
    """
    Tasks that loop perdiodically.
    """

    def __init__(self, bot):
        self.bot = bot
        self.tasks = {}
        self.task_channels = {}

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Runs when the cog is loaded
        """
        logger.info(f"{self} ready")
        try:
            self.ratemytakeaway_task.start()
            logger.info("ratemytakeaway_task started")
        except Exception as e:
            logger.error("Error starting ratemytakeaway_task : %s", e)

    @commands.command(aliases=["start task", "run task", "start", "run"])
    async def start_task(self, ctx, task_name: str, channel_id: int = None):
        """
        Start a task with the given name.
        """
        # Check if the task exists and is a Loop task
        task = getattr(self, task_name, None)
        if task is None or not isinstance(task, tasks.Loop):
            await ctx.send(f"No task found with the name {task_name}.")
            return

        # Check if the task is already running
        if task.is_running():
            await ctx.send(f"The task {task_name} is already running.")
            return

        if channel_id is not None:
            channel = self.bot.get_channel(channel_id)
            if channel is None:
                await ctx.send(f"Could not find channel with ID {channel_id}.")
                return

        # Start the task
        task.start()

        # Store the channel ID with the task
        self.tasks[task_name] = task
        self.task_channels[task_name] = (
            channel if channel_id is not None else ctx.channel.id
        )

        logger.info(
            "Task %s started by %s in channel %s",
            task_name,
            ctx.author.id,
            ctx.channel.id,
        )
        await ctx.send(f"The task {task_name} has been started.")

    @commands.command(aliases=["stop task", "end task", "stop", "end"])
    async def stop_task(self, ctx, task_name: str):
        """
        Stop a task with the given name.
        """
        task = self.tasks.get(task_name)
        if task is None:
            await ctx.send(f"Task '{task_name}' is not running in this channel")
            return

        try:
            task.cancel()
            del self.tasks[task_name]
            logger.info("Task %s stopped by %s", task_name, ctx.author.id)
            await ctx.send(f"Task '{task_name}' stopped")
        except Exception as e:
            logger.error("Error stopping task %s: %s", task_name, e)
            await ctx.send(f"ERROR {e}")

    @commands.command(aliases=["tasks", "status"])
    async def show_tasks_status(self, ctx):
        """
        Show the status and details of all tasks.
        """
        if not self.tasks:
            await ctx.send("No tasks have been started yet.")
            return

        for task_name, task in self.tasks.items():
            status = "running" if task.is_running() else "stopped"
            channel_id = self.task_channels.get(task_name)
            channel_info = f" (in channel <#{channel_id}>)" if channel_id else ""

            next_iteration = task.next_iteration
            if next_iteration is not None:
                next_iteration_str = next_iteration.strftime("%m-%d-%y %H:%M:%S")
                next_iteration_info = f", next run at {next_iteration_str}"
            else:
                next_iteration_info = ""

            await ctx.send(
                f"Task '{task_name}' is {status}{channel_info}{next_iteration_info}"
            )

    @tasks.loop(minutes=1)
    async def ratemytakeaway_task(self):
        """
        Task to fetch the latest video from Rate My Takeaway's channel
        """
        # Check if the current time is 6:05 PM to fetch the latest video
        now = datetime.now()
        if now.hour == 14 and now.minute == 5:
            # Get the channel ID associated with the task
            channel_id = self.task_channels.get("ratemytakeaway_task")  # Get channel ID
            if channel_id is None:
                logger.error(
                    "No channel associated with ratemytakeaway_task, but task is running. I would stop the task to avoid errors."
                )
                return

            channel = self.bot.get_channel(channel_id)

            if channel is None:
                logger.error("Could not find channel with ID - %s", channel_id)
                return

            # Check if the current time is 6:05 PM to fetch the latest video
            logger.info("Fetching latest video from Rate My Takeaway's channel")
            latest_video = query_latest_youtube_video_from_channel_id(
                RATEMYTAKEAWAY_YOUTUBE_CHANNEL_ID
            )
            logger.info(
                "Fetched the latest video from Rate My Takeaway's channel - %s",
                latest_video,
            )
            await channel.send(f"{latest_video['title']} - {latest_video['video_url']}")


async def setup(bot):
    """
    Add the cog to the bot
    """
    await bot.add_cog(Tasks(bot))
