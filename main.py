"""
This is the main file for the Discord bot.
It initializes the bot, loads all Cog files, and starts the bot.

Before running this file, make sure to set the environment variables PREFIX and DISCORD_TOKEN or else the bot will not work.
"""

import asyncio
import os
from pathlib import Path
from typing import Optional

import discord
from discord.ext import commands

from utils.logging_config import create_new_logger

# Initialize main logger for the bot
logger = create_new_logger(__name__)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("PREFIX")

# Check if the bot token and prefix are set as environment variables
if not DISCORD_TOKEN:
    logger.error("DISCORD_TOKEN environment variable not set")
    exit(1)
elif not PREFIX:
    logger.error("PREFIX environment variable not set")
    exit(1)
else:
    # Configure Discord bot intents and initialize the bot
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix=PREFIX, intents=intents, case_insensitive=True)
    BOT_TOKEN = DISCORD_TOKEN


async def main():
    """
    The main function that starts the Discord bot.
    """
    # Load all Cog files
    try:
        await load_all_cogs()
    except Exception as e:
        logger.error(
            "There was an error loading Cog files, the bot has been stopped: %s", e
        )
        return

    # Start the bot
    async with bot:
        logger.info("Starting bot...")
        await bot.start(BOT_TOKEN)


@bot.event
async def on_ready():
    """
    Runs once the bot establishes a connection with Discord.
    """
    logger.info("Logged in as %s", bot.user)


@bot.event
async def on_message(message):
    """
    This function is called whenever a message is sent in any channel of any guild.

    param: message - The message object that was sent in a channel
    """
    # Ignore messages from the bot itself and other bots to prevent infinite loops
    if message.author == bot.user or message.author.bot:
        return

    # Need this line at the end of on_message functions
    await bot.process_commands(message)


async def load_all_cogs():
    """
    Loads all Cog files from the /cogs directory.
    """
    for cog_file in Path("./cogs").rglob("*.py"):
        try:
            await bot.load_extension(f"cogs.{cog_file.stem}")
        except Exception as e:
            logger.error("%s - %s not loaded", e, cog_file.stem)

    logger.info("Loaded *%s* cogs", len(bot.cogs))


async def manage_cog(action: str, cog_name: str) -> tuple[bool, str]:
    """
    Helper function to manage cog operations (load, unload, reload).

    Returns: (success: bool, message: str)
    """
    try:
        if action == "load":
            await bot.load_extension(f"cogs.{cog_name}")
        elif action == "unload":
            await bot.unload_extension(f"cogs.{cog_name}")
        elif action == "reload":
            await bot.reload_extension(f"cogs.{cog_name}")
        return True, f"{cog_name}.py {action}ed"

    except commands.ExtensionAlreadyLoaded as e:
        logger.error("%s - %s already loaded", e, cog_name)
        return False, f"{cog_name}.py is already loaded\n{e}"
    except commands.ExtensionNotLoaded as e:
        logger.error("%s - %s is not loaded", e, cog_name)
        return False, f"{cog_name}.py is not loaded\n{e}"
    except commands.ExtensionNotFound as e:
        logger.error("%s - %s does not exist", e, cog_name)
        return False, f"{cog_name}.py does not exist\n{e}"
    except Exception as e:
        logger.error("%s", e)
        return False, f"{cog_name}.py could not be {action}ed\n{e}"


@bot.command(help="Load, unload, or reload cogs")
@commands.has_permissions(administrator=True)
async def cog(ctx, action: str, cog_name: str = ""):
    """
    Unified cog management command.

    Usage:
    !cog load <cog_name>
    !cog unload <cog_name>
    !cog reload <cog_name> (or just !cog reload to reload all)
    """
    valid_actions = {"load", "unload", "reload"}

    if action not in valid_actions:
        await ctx.send(f"```Invalid action. Use: {', '.join(valid_actions)}```")
        return

    if action == "reload" and cog_name == "":
        # Reload all cogs
        reloaded, failed = [], []
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                success, _ = await manage_cog("reload", filename[:-3])
                (reloaded if success else failed).append(filename)

        await ctx.send(
            f"```Reloaded: {', '.join(reloaded) or 'None'}\n"
            f"Failed: {', '.join(failed) or 'None'}```"
        )
        return

    if not cog_name:
        await ctx.send(f"```Cog name required for {action} action```")
        return

    success, message = await manage_cog(action, cog_name)
    await ctx.send(f"```{message}```")


@bot.command(name="sync")
@commands.guild_only()
@commands.has_permissions(administrator=True)
async def sync_command(ctx, spec: Optional[str] = None):
    """
    Syncs slash commands with Discord.

    Without arguments, syncs current guild commands
    `!sync global` - sync global commands (can take up to 1 hour to appear)
    `!sync clear` - clear all commands from the current guild
    `!sync clear global` - clear all global commands (dangerous!)
    """
    if spec not in [None, "global", "clear", "clear global"]:
        await ctx.send(
            "Invalid option. Use `!sync`, `!sync global`, `!sync clear`, or `!sync clear global`"
        )
        return

    if spec is None:
        # Sync to current guild
        synced = await ctx.bot.tree.sync(guild=ctx.guild)
        logger.info(
            "Synced %d commands to guild %s (%d)", len(synced), ctx.guild, ctx.guild.id
        )
        await ctx.send(f"Synced {len(synced)} commands to the current guild.")
        return

    elif spec == "global":
        # Sync globally (takes up to 1 hour to propagate)
        ctx.bot.tree.copy_global_to(guild=ctx.guild)
        await ctx.bot.tree.sync(guild=None)
        logger.info("Synced commands globally (requested by %s)", ctx.message.author)
        await ctx.send(
            "Synced commands globally. This can take up to 1 hour to take effect."
        )
        return

    elif spec == "clear":
        # Clear commands from current guild
        ctx.bot.tree.clear_commands(guild=ctx.guild)
        await ctx.bot.tree.sync(guild=ctx.guild)
        logger.info("Cleared all commands from guild %s (%d)", ctx.guild, ctx.guild.id)
        await ctx.send("Cleared all commands from the current guild.")
        return

    elif spec == "clear global":
        # Clear global commands
        ctx.bot.tree.clear_commands(guild=None)
        await ctx.bot.tree.sync(guild=None)
        logger.info("Cleared all global commands (requested by %s)", ctx.message.author)
        await ctx.send(
            "Cleared all global commands. This can take up to 1 hour to take effect."
        )
        return


asyncio.run(main())
