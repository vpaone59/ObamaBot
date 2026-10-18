"""
Reddit API Cog for ObamaBot https://github.com/vpaone59
"""

import datetime
import os
import random
from typing import Optional

import asyncpraw
import asyncprawcore
import discord
from discord.ext import commands

from utils.logging_config import create_new_logger

logger = create_new_logger(__name__)

CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USER_AGENT = os.getenv("REDDIT_USER_AGENT")

# Short source key -> subreddit name, used by the food poll commands
FOOD_SUBREDDITS = {
    "sfp": "shittyfoodporn",
    "fporn": "FoodPorn",
    "bake": "Baking",
    "food": "food",
}
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp")


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
        Runs when the cog is loaded
        """
        logger.info("%s ready", self.__cog_name__)

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

    async def create_food_poll(
        self, ctx: commands.Context, subreddit_name: str
    ) -> None:
        """
        Post a random hot image from the given subreddit as an up/down vote poll
        """
        try:
            subreddit = await self.reddit.subreddit(subreddit_name)

            # Get 50 hot posts to have a good selection
            posts = [post async for post in subreddit.hot(limit=50)]

            # Keep only SFW, non-pinned posts that link directly to an image
            image_posts = [
                post
                for post in posts
                if not post.stickied
                and not post.over_18
                and (
                    post.url.endswith(IMAGE_EXTENSIONS)
                    or "i.redd.it" in post.url
                    or "i.imgur.com" in post.url
                )
            ]

            if not image_posts:
                await ctx.send(f"No image posts found in r/{subreddit_name}")
                return

            selected_post = random.choice(image_posts)

            embed = discord.Embed(color=0xFF6B35)
            embed.add_field(
                name=f"{selected_post.title[:150]}{'...' if len(selected_post.title) > 150 else ''}",
                value=f"[r/{subreddit_name}](https://reddit.com/r/{subreddit_name}) | 👤 u/{selected_post.author} | ⬆️ {selected_post.score}\n[View Post](https://reddit.com{selected_post.permalink})",
                inline=False,
            )
            embed.set_image(url=selected_post.url)

            message = await ctx.send(embed=embed)

            # Add voting reactions
            await message.add_reaction("⬆️")
            await message.add_reaction("⬇️")

        except asyncprawcore.exceptions.AsyncPrawcoreException:
            logger.exception(
                "Reddit error creating food poll from r/%s", subreddit_name
            )
            await ctx.send(
                f"Couldn't reach r/{subreddit_name} right now, try again later."
            )
        except discord.DiscordException:
            logger.exception(
                "Discord error creating food poll from r/%s", subreddit_name
            )

    @commands.command(aliases=["fp", "foodpoll"])
    async def food_poll(
        self, ctx: commands.Context, source: Optional[str] = None
    ) -> None:
        """
        Create a food poll from a subreddit, e.g. .fp baking, or a random one with .fp
        """
        if source is None:
            await self.create_food_poll(
                ctx, random.choice(list(FOOD_SUBREDDITS.values()))
            )
            return

        if source.lower() not in FOOD_SUBREDDITS:
            choices = ", ".join(
                f"`{key}` (r/{name})" for key, name in FOOD_SUBREDDITS.items()
            )
            await ctx.send(
                f"Usage: `.fp [source]` (no source picks one at random).\nSources: {choices}"
            )
            return

        await self.create_food_poll(ctx, FOOD_SUBREDDITS[source.lower()])

    @commands.command(aliases=["sfp"])
    async def shitty_food_poll(self, ctx: commands.Context) -> None:
        """
        Create a food poll from r/shittyfoodporn
        """
        await self.create_food_poll(ctx, FOOD_SUBREDDITS["sfp"])

    @commands.command(aliases=["fporn"])
    async def food_porn_poll(self, ctx: commands.Context) -> None:
        """
        Create a food poll from r/FoodPorn
        """
        await self.create_food_poll(ctx, FOOD_SUBREDDITS["fporn"])

    @commands.command(aliases=["bake"])
    async def baking_poll(self, ctx: commands.Context) -> None:
        """
        Create a food poll from r/Baking
        """
        await self.create_food_poll(ctx, FOOD_SUBREDDITS["bake"])

    @commands.command(aliases=["food"])
    async def food_sub_poll(self, ctx: commands.Context) -> None:
        """
        Create a food poll from r/food
        """
        await self.create_food_poll(ctx, FOOD_SUBREDDITS["food"])


async def setup(bot):
    """
    Adds the cog to the bot
    """
    if not all([CLIENT_ID, CLIENT_SECRET, USER_AGENT]):
        logger.error("Reddit API credentials not set. NotReddit cog not loaded.")
        return
    await bot.add_cog(NotReddit(bot))
