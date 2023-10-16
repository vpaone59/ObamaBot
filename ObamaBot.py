"""
Vincent Paone
Project began 4/20/2022 --
ObamaBot - main file. Run this file to start the bot.

There is no serious political offiliation. This is all in good fun.
"""

from discord.ext.commands import Greedy, Context  # or a subclass of yours
from typing import Literal, Optional
import logging
import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=os.getenv("PREFIX"), intents=intents)

"""
Logger setup
creates a logger object
creates a stream handler for printing logs to the shell
creates a file handler for saving logs with date/time to bot.log
"""
LOG_FILE = "bot.log"
if not os.path.exists(LOG_FILE):  # Check if the file does not exist
    with open(LOG_FILE, "w", encoding="utf-8"):  # Create the file if it does not exist
        pass

# Set the logging level to INFO
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)
# Configure the logger to send logs to stdout
# stream_handler = logging.StreamHandler()
# logger.addHandler(stream_handler)
# Configure the logger to save logs to a file
file_handler = logging.FileHandler("bot.log")
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(file_handler)


async def main():
    """
    Main function that starts the Bot
    """
    async with bot:
        await bot.start(os.getenv("DISCORD_TOKEN"))
        logger.info(f'Starting bot with {os.getenv("DISCORD_TOKEN")}')
        # on_ready will run next


@bot.event
async def on_ready():
    """
    Runs once the bot establishes a connection with Discord
    """
    logger.info(f"Logged in as {bot.user}")
    try:
        await load_all_cogs()
    except Exception as e:
        logger.error(f"Bot not ready: {e}")


@bot.event
async def on_message(message):
    """
    every time there is a message in any channel in any guild, this runs
    param message - The message that was last sent to the channel
    """
    # ignore messages sent from the bot itself and other bots
    # prevents infinite replying
    if message.author == bot.user or message.author.bot:
        return

    # messageAuthor = message.author
    # user_message = str(message.content)

    # necessary to process the bot's message
    await bot.process_commands(message)


async def load_all_cogs():
    """
    Function for loading all Cog .py files in /cogs directory
    """
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                logger.info(f"{filename} loaded")
            except Exception as e:
                logger.error({e})


@bot.command(aliases=["load"], help="Load a Cog file")
@commands.has_permissions(administrator=True)
async def load_cog(ctx, cog_name):
    """
    Load a Cog file, do -load "name of cog file"
    Only a user with Administrator role should be able to run this command
    param: ctx - The context in which the command has been executed
    param: extension - The name of the Cog file you want to load
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
    Unload a Cog file, do -unload "name of cog file"
    Only a user with Administrator role should be able to run this command
    param: ctx- The context of which the command is entered
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
