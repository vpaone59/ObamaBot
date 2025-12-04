"""
Custom Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

This Cog is custom made for a specific server and will not work in normal servers.
"""

import os
import discord
from discord.ext import commands
from logging_config import create_new_logger

logger = create_new_logger(__name__)


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
        string_message = str(message.content)

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


async def setup(bot):
    await bot.add_cog(Friends(bot))
