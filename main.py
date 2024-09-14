import os
import asyncio
from typing import Literal, Optional
import discord
from dotenv import load_dotenv
from discord.ext.commands import Greedy, Context  # or a subclass of yours
from discord.ext import commands
from logging_config import create_new_logger
from db_helper import initialize_db

# Initialize main logger for the bot
logger = create_new_logger(__name__)

# Load environment variables from .env file
load_dotenv()
logger.info("Environment variables loaded")

# Configure Discord bot intents and grab token from environment variables
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=os.getenv("PREFIX"), intents=intents)
BOT_TOKEN = os.getenv("DISCORD_TOKEN")


async def main():
    """
    The main function that starts the Discord bot.
    """

    # Initialize the database
    try:
        logger.info("Initializing database")
        initialize_db()
    except Exception as e:
        logger.error("Failed to initialize database: %s", e)
        raise e

    # Load all Cog files
    try:
        await load_all_cogs()
    except Exception as e:
        logger.error("Bot not ready: %s", e)

    # Start the bot
    async with bot:
        logger.info("TOKEN grabbed\n Starting bot")
        await bot.start(BOT_TOKEN)


@bot.event
async def on_ready():
    """
    Runs once the bot establishes a connection with Discord.

    Load all cogs into the bot
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
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                logger.info("%s loaded", filename)
            except Exception as e:
                logger.error("%s - %s not loaded", e, filename)


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
        await ctx.send(f"```{cog_name}.py is already loaded\n{e}```")
        logger.error("%s - %s already loaded", e, cog_name)

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


@bot.command()
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

    param: ctx - The context in which the command is entered
    param: guilds - The guilds to sync the commands to
    param: spec - The specification for syncing the commands
    """
    logger.info("Syncing commands")

    if not guilds:
        if spec == "~":
            # Sync to the current guild
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            # Sync globally
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            # Clear the current guild's commands
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        logger.info("Synced %s commands", len(synced))
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
