"""
Reddit API Cog for ObamaBot https://github.com/vpaone59
"""

import os
import datetime
import random
from discord.ext import commands
import asyncpraw

CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USER_AGENT = os.getenv("REDDIT_USER_AGENT")


class NotReddit(commands.Cog):
    """
    Reddit API thingy
    """

    def __init__(self, bot):
        self.bot = bot
        self.reddit = asyncpraw.Reddit(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            user_agent=USER_AGENT,
        )

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Prints a message when the bot is ready
        """
        print(f"{self} ready")

    async def is_nsfw(self, subreddit):
        """
        Checks if the subreddit is NSFW
        """
        await subreddit.load()
        return subreddit.over18

    @commands.command(aliases=["lp", "get_latest_post"])
    async def get_latest_post_from_subreddit(self, ctx, subreddit):
        """
        Get the most recent post on a non-NSFW subreddit
        """
        subreddit_param = str(subreddit)

        try:
            # Fetch the latest post from the specified subreddit
            subreddit = await self.reddit.subreddit(subreddit_param)
            # Check to see if the subreddit is NSFW
            if await self.is_nsfw(subreddit):
                await ctx.send("NSFW subreddits are not allowed.")
                return

            # Fetch latest post
            async for post in subreddit.new(limit=1):
                submission_datetime = datetime.datetime.fromtimestamp(post.created_utc)
                time_difference = datetime.datetime.utcnow() - submission_datetime

                # Calculate the hours and minutes
                hours_ago = int(time_difference.total_seconds() // 3600)
                minutes_ago = int((time_difference.total_seconds() % 3600) // 60)

                # Display the time difference based on the condition
                if hours_ago >= 1:
                    await ctx.send(
                        f"Latest post from r/{post.subreddit} {hours_ago} hours ago:\nUpvotes: {post.score}\nTitle: {post.title}\nOP: {post.author}\nURL: {post.url}"
                    )
                else:
                    await ctx.send(
                        f"Latest post from r/{post.subreddit} {minutes_ago} minutes ago:\nUpvotes: {post.score}\nTitle: {post.title}\nOP: {post.author}\nURL:{post.url}"
                    )

        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @commands.command(aliases=["rp", "get_random_post"])
    async def get_random_post_from_prev_day(self, ctx, subreddit):
        """
        Get a random Reddit post from a non-NSFW subreddit within the last 24 hours
        """
        subreddit_param = str(subreddit)

        try:
            # Fetch the latest post from the specified subreddit
            subreddit = await self.reddit.subreddit(subreddit_param)
            # Check to see if the subreddit is NSFW
            if await self.is_nsfw(subreddit):
                await ctx.send("NSFW subreddits are not allowed.")
                return

            # Fetch 100 latest posts
            posts = [post async for post in subreddit.new(limit=100)]

            # Filter posts from the last 24 hours
            current_time = datetime.datetime.utcnow()
            posts_within_last_24h = [
                post
                for post in posts
                if (
                    current_time - datetime.datetime.fromtimestamp(post.created_utc)
                ).total_seconds()
                <= 86400
            ]

            if not posts_within_last_24h:
                await ctx.send(
                    "No posts found within the last 24 hours from the specified subreddit."
                )
                return

            # Choose a random post from the filtered list
            random_post = random.choice(posts_within_last_24h)
            submission_datetime = datetime.datetime.fromtimestamp(
                random_post.created_utc
            )
            time_difference = current_time - submission_datetime

            # Calculate the hours and minutes
            hours_ago = int(time_difference.total_seconds() // 3600)
            minutes_ago = int((time_difference.total_seconds() % 3600) // 60)

            # Display the time difference based on the condition
            if hours_ago >= 1:
                await ctx.send(
                    f"Random post from r/{random_post.subreddit} {hours_ago} hours ago:\nUpvotes: {random_post.score}\nTitle: {random_post.title}\nOP: {random_post.author}\nURL: {random_post.url}"
                )
            else:
                await ctx.send(
                    f"Random post from r/{random_post.subreddit} {minutes_ago} minutes ago:\nUpvotes: {random_post.score}\nTitle: {random_post.title}\nOP: {random_post.author}\nURL: {random_post.url}"
                )

        except Exception as e:
            await ctx.send(f"An error occurred: {e}")


async def setup(bot):
    """
    Adds the cog to the bot
    """
    await bot.add_cog(NotReddit(bot))
