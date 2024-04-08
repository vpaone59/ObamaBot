"""
Vincent Paone
Project began 4/20/2022 --
ObamaBot - Main file. Run this file to start the bot.

There is no serious political affiliation. This is all in good fun.
"""

from discord.ext.commands import Greedy, Context  # or a subclass of yours
from typing import Literal, Optional
from logging_config import setup_logging
import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Configure logging using the setup_logging function
logger = setup_logging(__name__)

# Load environment variables from a .env file
load_dotenv()

# Configure Discord bot intents and initialize a placeholder logger
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=os.getenv("PREFIX"), intents=intents)


async def main():
    """
    The main function that starts the Discord bot.
    """
    async with bot:
        await bot.start(os.getenv("DISCORD_TOKEN"))
        logger.info("Starting bot with %s", os.getenv("DISCORD_TOKEN"))
        # on_ready event will be called next


@bot.event
async def on_ready():
    """
    Runs once the bot establishes a connection with Discord.
    """
    logger.info(f"Logged in as {bot.user}")

    try:
        await load_all_cogs()
    except Exception as e:
        logger.error(f"Bot not ready: {e}")


@bot.event
async def on_message(message):
    """
    This function is called whenever a message is sent in any channel of any guild.

    Args:
        message: The message object containing information about the sent message.
    """
    # Ignore messages from the bot itself and other bots to prevent infinite loops
    if message.author == bot.user or message.author.bot:
        return

    # Process the message using the bot's command processing functionality
    await bot.process_commands(message)


async def load_all_cogs():
    """
    Loads all Cog (Python) files from the /cogs directory.
    """
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                logger.info(f"{filename} loaded")
            except Exception as e:
                logger.error({e})


@bot.command(aliases=["load"], help="Loads a Cog file")
@commands.has_permissions(administrator=True)
async def load_cog(ctx, cog_name):
    """
    Loads a specific Cog file.

    param: ctx - The context object containing information about the command invocation.
    param: cog_name - The name of the Cog file to load (without the .py extension).
    """
    try:
        await bot.load_extension(f"cogs.{cog_name}")
        await ctx.send(f"```{cog_name}.py loaded```")
    except commands.ExtensionAlreadyLoaded as e:
        logger.error({e})
        await ctx.send(f"```{cog_name}.py is already loaded\n{e}```")
    except commands.ExtensionNotFound as e:
        logger.error({e})
        await ctx.send(f"```{cog_name}.py does not exist\n{e}```")


@bot.command(aliases=["unload"], help="Unload a Cog file")
@commands.has_permissions(administrator=True)
async def unload_cog(ctx, cog_name):
    """
    Unload a Cog file
    Only a user with Administrator role should be able to run this command
    param: ctx - The context of which the command is entered
    param: extension - The name of the Cog file to unload
    """
    try:
        await bot.unload_extension(f"cogs.{cog_name}")
        await ctx.send(f"```{cog_name}.py unloaded```")
    except commands.ExtensionNotLoaded as e:
        logger.error({e})
        await ctx.send(f"```{cog_name}.py is not loaded\n{e}```")
    except commands.ExtensionNotFound as e:
        logger.error({e})
        await ctx.send(f"```{cog_name}.py does not exist\n{e}```")


@bot.command(aliases=["rl"], help="Reloads all Cog files")
@commands.has_permissions(administrator=True)
async def reload_cog(ctx, cog_name=""):
    """
    Reload a specific Cog file or all Cogs by default
    Only a user with Administrator role should be able to run this command
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
                    logger.error({e})
                    failed += " - " + filename
        await ctx.send(
            f"```These Cogs were reloaded: {reloaded_cogs}\n\nThese Cogs failed to reload: {failed}```"
        )
    else:
        try:
            await bot.reload_extension(f"cogs.{cog_name}")
            await ctx.send(f"```{cog_name}.py reloaded```")
        except commands.ExtensionNotFound as e:
            logger.error({e})
            await ctx.send(f"```{cog_name}.py not in directory\n{e}```")
        except Exception as e:
            logger.error({e})
            await ctx.send(f"```{cog_name}.py could not be reloaded \n{e}```")


@bot.command()
# @commands.guild_only()
# @commands.is_owner()
async def sync(
    ctx: Context,
    guilds: Greedy[discord.Object],
    spec: Optional[Literal["~", "*", "^"]] = None,
) -> None:
    """
    Sync Slash Commands Globally to the bot
    When to sync
    When you add a new command.
    When you remove a command.
    When a command's name or description changes.
    When the callback's parameters change.
    This includes parameter names, types or descriptions.
    Also when you add or remove a parameter.
    If you change a global to a guild command, or vice versa.
    NOTE: If you do this, you will need to sync both global and to that guild to reflect the change.
    These are currently the only times you should re-sync.
    """
    print("running")

    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


asyncio.run(main())
