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
from logging_config import create_new_logger

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
    bot = commands.Bot(command_prefix=PREFIX, intents=intents)
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
    for cog_file in Path("./app/cogs").rglob("*.py"):
        try:
            await bot.load_extension(f"cogs.{cog_file.stem}")
        except Exception as e:
            logger.error("%s - %s not loaded", e, cog_file.stem)

    logger.info("Loaded *%s* cogs", len(bot.cogs))


@bot.command(aliases=["load"], help="Loads a Cog file")
@commands.has_permissions(administrator=True)
async def load_cog(ctx, cog_name):
    """
    Loads a specific Cog file.

    param: ctx - The context in which the command is entered
    param: cog_name - The name of the Cog file to load
    """
    try:
        await bot.load_extension(f"cogs.{cog_name}")
        await ctx.send(f"```{cog_name}.py loaded```")

    except commands.ExtensionAlreadyLoaded as e:
        logger.error("%s - %s already loaded", e, cog_name)
        await ctx.send(f"```{cog_name}.py is already loaded\n{e}```")

    except commands.ExtensionNotFound as e:
        logger.error("%s - %s does not exist", e, cog_name)
        await ctx.send(f"```{cog_name}.py does not exist\n{e}```")


@bot.command(aliases=["unload"], help="Unload a Cog file")
@commands.has_permissions(administrator=True)
async def unload_cog(ctx, cog_name):
    """
    Unload a Cog file

    param: ctx - The context of which the command is entered
    param: cog_name - The name of the Cog file to unload
    """
    try:
        await bot.unload_extension(f"cogs.{cog_name}")
        await ctx.send(f"```{cog_name}.py unloaded```")

    except commands.ExtensionNotLoaded as e:
        logger.error("%s - %s is not loaded", e, cog_name)
        await ctx.send(f"```{cog_name}.py is not loaded\n{e}```")

    except commands.ExtensionNotFound as e:
        logger.error("%s - %s does not exist", e, cog_name)
        await ctx.send(f"```{cog_name}.py does not exist\n{e}```")


@bot.command(aliases=["rl"], help="Reloads a specific Cog or all Cogs by default")
@commands.has_permissions(administrator=True)
async def reload_cog(ctx, cog_name=""):
    """
    Reloads a specific Cog file or all Cogs by default

    param: ctx - The context in which the command has been executed
    param: cog_name - The name of the Cog file to reload
    """
    if cog_name == "":
        reloaded_cogs = ""
        failed = ""
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                try:
                    await bot.reload_extension(f"cogs.{filename[:-3]}")
                    reloaded_cogs += " - " + filename
                except Exception as e:
                    logger.error("%s", e)
                    failed += " - " + filename
        await ctx.send(
            f"```These Cogs were reloaded: {reloaded_cogs}\n\nThese Cogs failed to reload: {failed}```"
        )
    else:
        try:
            await bot.reload_extension(f"cogs.{cog_name}")
            await ctx.send(f"```{cog_name}.py reloaded```")

        except commands.ExtensionNotFound as e:
            logger.error("%s", e)
            await ctx.send(f"```{cog_name}.py not in directory\n{e}```")

        except Exception as e:
            logger.error("%s", e)
            await ctx.send(f"```{cog_name}.py could not be reloaded \n{e}```")


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
