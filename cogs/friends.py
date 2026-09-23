"""
Custom Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

This Cog is custom made for specific servers and will not work in normal servers.
Includes guild-specific inside-joke features like the frank/Danny DeVito trigger.
"""

import asyncio
import json
import os
import random
from urllib import parse, request

import discord
from discord.ext import commands

from utils.logging_config import create_new_logger

logger = create_new_logger(__name__)

# Guild-specific env vars
WORK_GUILD_ID = os.getenv("WORK_GUILD_ID")
FRANK_CHANNEL_ID = os.getenv("FRANK_CHANNEL_ID")

# Gif API keys (Klipy primary, Giphy fallback)
KLIPY_KEY = os.getenv("KLIPY_KEY")
KLIPY_API_URL = "https://api.klipy.io/gifs/search"
GIPHY_KEY = os.getenv("GIPHY_KEY")
GIPHY_SEARCH_URL = "http://api.giphy.com/v1/gifs/search"

GIF_SEARCH_QUERY = "danny devito"
FRANK_TRIGGER_PHRASES = {"frank", "!frank"}


class Friends(commands.Cog):
    """
    Custom commands made for specific guilds
    For friends :)
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.user_reactions = {
            "toggle": False,
            "discord_user_id": None,
        }
        self.friend_guilds_locked = False
        self.work_guild_id = int(WORK_GUILD_ID) if WORK_GUILD_ID else None
        self.frank_channel_id = int(FRANK_CHANNEL_ID) if FRANK_CHANNEL_ID else None
        logger.info(
            "Friends cog initialized with reactions: %s, guild_lock: %s",
            self.user_reactions["toggle"],
            self.friend_guilds_locked,
        )

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Runs when the cog is loaded
        """
        logger.info("%s ready", self.__cog_name__)

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        whenever a message is sent this Cog will listen and execute code below
        """
        if message.author == self.bot.user or message.author.bot:
            return

        string_message = str(message.content)

        # Check for frank trigger first (works regardless of prefix)
        await self._check_frank_trigger(message)

        # return whenever a prefix is detected without a command attached
        if string_message.startswith(f"{os.getenv('PREFIX')}"):
            return

        if self.friend_guilds_locked:
            return

        # Message reactions for a user
        if (
            self.user_reactions["toggle"]
            and self.user_reactions["discord_user_id"] == message.author.id
        ):
            await message.add_reaction("♿")

    @commands.command(aliases=["togr"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def toggle_message_reactions(self, ctx, user: discord.Member = None):
        """
        Toggle reactions for a user's messages.
        """

        try:
            # If no user is mentioned when the command is run
            if len(ctx.message.mentions) == 0:
                # If the user_reactions flag is True, set it to False and clear the user ID
                if self.user_reactions["toggle"]:
                    # Disable reactions and clear the user ID
                    self.user_reactions["toggle"] = False
                    self.user_reactions["discord_user_id"] = None
                    await ctx.send("Message reactions disabled.")

                else:
                    await ctx.send("Please @ mention a user.")

                return

            else:
                # Toggle reactions for the user mentioned
                self.user_reactions["toggle"] = not self.user_reactions["toggle"]
                # Get the user ID from the mention and store it
                user_id = ctx.message.mentions[0].id
                self.user_reactions["discord_user_id"] = user_id

                if self.user_reactions["toggle"]:
                    await ctx.send(f"Message reactions enabled for user: {user}")
                else:
                    await ctx.send("Message reactions disabled.")

        except Exception as e:
            logger.error("Error toggling message reactions: %s", e)

    @commands.command(aliases=["lock", "lockguilds"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def toggle_friend_guilds_lock(self, ctx):
        """
        Toggle friend guilds lock. Prevents commands in this Cog from being used in non-friend guilds.
        You can edit the list of friend guilds in the .env file.
        """
        self.friend_guilds_locked = not self.friend_guilds_locked
        if self.friend_guilds_locked:
            await ctx.send("Friend guilds locked.")
            logger.info("Friend guilds locked.")
        else:
            await ctx.send("Friend guilds unlocked.")
            logger.info("Friend guilds unlocked.")

    async def _check_frank_trigger(self, message: discord.Message):
        """
        Check if message is a frank trigger ("!frank" or "frank" with optional "@here").
        Runs even when message starts with prefix, since "!frank" is not a registered command.
        """
        logger.debug(
            "_check_frank_trigger called | guild_id: %s | channel_id: %s",
            message.guild.id if message.guild else None,
            message.channel.id,
        )

        if self.work_guild_id is None or self.frank_channel_id is None:
            logger.debug(
                "Guild/channel IDs not configured | work_guild_id: %s | frank_channel_id: %s",
                self.work_guild_id,
                self.frank_channel_id,
            )
            return

        if message.guild is None or message.guild.id != self.work_guild_id:
            logger.debug(
                "Guild mismatch | expected: %s | got: %s",
                self.work_guild_id,
                message.guild.id if message.guild else None,
            )
            return

        if message.channel.id != self.frank_channel_id:
            logger.debug(
                "Channel mismatch | expected: %s | got: %s",
                self.frank_channel_id,
                message.channel.id,
            )
            return

        # Strip prefix (if present), "@here" (if present), and whitespace
        content = message.content.strip()
        prefix = os.getenv("PREFIX", "!")
        # Only strip prefix if message starts with it
        if content.startswith(prefix):
            content = content[len(prefix) :].strip()
        # Strip "@here" if present
        if content.lower().startswith("@here"):
            content = content[len("@here") :].strip()

        logger.debug(
            "Checking frank trigger | content: '%s' | trigger phrases: %s",
            content.lower(),
            FRANK_TRIGGER_PHRASES,
        )
        if content.lower() not in FRANK_TRIGGER_PHRASES:
            logger.debug("Content doesn't match trigger phrases")
            return

        logger.info("Frank trigger matched! Fetching GIF...")
        gif_url = await self._get_devito_gif()
        logger.info("GIF URL fetched: %s", gif_url)

        if gif_url:
            try:
                await message.channel.send(gif_url)
                logger.info("Frank GIF sent successfully")
            except Exception as e:
                logger.exception("Failed to send frank GIF: %s", e)
        else:
            try:
                await message.channel.send(
                    "Couldn't find a Frank GIF right now. Frank!"
                )
                logger.info("Frank error message sent")
            except Exception as e:
                logger.exception("Failed to send frank error message: %s", e)

    async def _get_devito_gif(self) -> str | None:
        """
        Search for a Danny DeVito GIF, trying Klipy first, then Giphy as fallback.
        """
        logger.info(
            "Starting GIF fetch | KLIPY_KEY set: %s | GIPHY_KEY set: %s",
            bool(KLIPY_KEY),
            bool(GIPHY_KEY),
        )

        # Try Klipy first if available
        if KLIPY_KEY:
            logger.info("Attempting Klipy API...")
            url = await asyncio.get_event_loop().run_in_executor(
                None, self._fetch_gif_from_klipy
            )
            logger.info("Klipy result: %s", url)
            if url:
                return url

        # Fall back to Giphy
        if GIPHY_KEY:
            logger.info("Attempting Giphy API (fallback)...")
            url = await asyncio.get_event_loop().run_in_executor(
                None, self._fetch_gif_from_giphy
            )
            logger.info("Giphy result: %s", url)
            if url:
                return url

        logger.error("No GIF APIs configured (KLIPY_KEY and GIPHY_KEY both missing)")
        return None

    @staticmethod
    def _fetch_gif_from_klipy() -> str | None:
        """
        Search Klipy for a Danny DeVito GIF and return the URL, or None on failure.
        Blocking call, run via run_in_executor.
        """
        try:
            logger.debug("Klipy: Building request...")
            params = parse.urlencode(
                {
                    "query": GIF_SEARCH_QUERY,
                    "api_key": KLIPY_KEY,
                    "limit": "25",
                }
            )
            url = f"{KLIPY_API_URL}?{params}"
            logger.debug("Klipy: Requesting %s", url)

            with request.urlopen(url, timeout=10) as response:
                if response.status != 200:
                    logger.error("Klipy API returned status code: %s", response.status)
                    return None

                data = json.loads(response.read())
                logger.debug("Klipy: Response keys: %s", list(data.keys()))
                results = data.get("gifs") or data.get("data")
                if not results:
                    logger.info(
                        "No GIFs found on Klipy for query: %s", GIF_SEARCH_QUERY
                    )
                    return None

                selection = random.choice(results)
                url = selection.get("url") or selection.get("embed_url")
                logger.info("Klipy: Found URL: %s", url)
                return url

        except Exception:
            logger.exception("Error fetching GIF from Klipy")
            return None

    @staticmethod
    def _fetch_gif_from_giphy() -> str | None:
        """
        Search Giphy for a Danny DeVito GIF and return the URL, or None on failure.
        Blocking call, run via run_in_executor.
        """
        try:
            logger.debug("Giphy: Building request...")
            params = parse.urlencode(
                {
                    "q": GIF_SEARCH_QUERY,
                    "api_key": GIPHY_KEY,
                    "limit": "25",
                    "rating": "pg-13",
                }
            )
            url = f"{GIPHY_SEARCH_URL}?{params}"
            logger.debug("Giphy: Requesting %s", url)

            with request.urlopen(url, timeout=10) as response:
                if response.status != 200:
                    logger.error("Giphy API returned status code: %s", response.status)
                    return None

                data = json.loads(response.read())
                logger.debug("Giphy: Response keys: %s", list(data.keys()))
                results = data.get("data")
                if not results:
                    logger.info(
                        "No GIFs found on Giphy for query: %s", GIF_SEARCH_QUERY
                    )
                    return None

                selection = random.choice(results)
                url = selection.get("embed_url") or selection.get("url")
                logger.info("Giphy: Found URL: %s", url)
                return url

        except Exception:
            logger.exception("Error fetching GIF from Giphy")
            return None


async def setup(bot):
    await bot.add_cog(Friends(bot))
