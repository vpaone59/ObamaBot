"""
Vincent Paone
Project began 4/20/2022 --
ObamaBot - main file. Run this file to start the bot.

There is no serious political offiliation. This is all in good fun.
"""

import os  # os calls
import time
import asyncio
import discord  # needed
from discord.ext import commands  # needed
from dotenv import load_dotenv  # to load .env variables

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=os.getenv("PREFIX"), intents=intents)


async def main():
    """
    main function that starts the Bot
    """
    async with bot:
        # load cogs
        await load_all()
        await bot.start(os.getenv("DISCORD_TOKEN"))
        # on_ready will run next


@bot.event
async def on_ready():
    """
    runs once the bot establishes a connection with Discord
    """
    print(f'Logged in as {bot.user}')
    try:
        print("Bot ready")
    except Exception as e:
        print(f'Bot not ready {e}')


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


def load_Cogs():
    """
    Function to load all Cogs that live in the cogs folder
    Ran on Bot startup
    """
    for filename in os.listdir(os.getcwd() + '/cogs'):
        if filename.endswith('.py'):
            try:
                # -3 cuts the .py extension from filename
                bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'Cog {filename} loaded')
            except commands.ExtensionAlreadyLoaded:
                print(f'Cog {filename} aleady loaded')
            except Exception as e:
                print(f'Cog {filename} NOT loaded\n{e}')


def unload_Cogs():
    """
    Function to unload all Cogs in the cogs folder
    Runs on -rl all
    """
    for filename in os.listdir(os.getcwd() + '/cogs'):
        if filename.endswith('.py'):
            try:
                bot.unload_extension(f'cogs.{filename[:-3]}')
                print(f'Cog {filename} unloaded successfully')
            except commands.ExtensionNotLoaded:
                print(f'Cog {filename} is not loaded')


async def load_all():
    """
    goes through the /cogs dir and tries to load \
    every file with .py extension
    """
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'{filename} loaded')
            except Exception as e:
                print(f'Could not load {filename}\n{e}')


@bot.command()
@commands.has_permissions(administrator=True)
async def load(ctx, extension):
    """
    Load a Cog file, do -load "name of cog file"
    only admin should be able to run this
    param: ctx - The context in which the command has been executed
    param: extension - The name of the Cog file you want to load
    """
    try:
        await bot.load_extension(f'cogs.{extension}')
        await ctx.send(f'```Cog {extension}.py loaded```')
    except commands.ExtensionAlreadyLoaded:
        await ctx.send(f'```{extension}.py is already loaded```')
    except commands.ExtensionNotFound:
        await ctx.send(f'```{extension}.py does not exist```')


@bot.command()
@commands.has_permissions(administrator=True)
async def unload(ctx, extension):
    """
    Unload a Cog file, do -unload "name of cog file"
    only admin should be able to run this
    param: ctx- The context of which the command is entered
    param: extension - The name of the Cog file to unload
    """
    try:
        await bot.unload_extension(f'cogs.{extension}')
        await ctx.send(f'```Cog {extension}.py unloaded```')
    except commands.ExtensionNotLoaded:
        await ctx.send(f'```{extension}.py is not loaded```')
    except commands.ExtensionNotFound:
        await ctx.send(f'```{extension}.py does not exist```')


@bot.command(aliases=['rf', 'rl'], description='Reloads all Cog files')
@commands.has_permissions(administrator=True)
async def refresh(ctx, extension):
    """
    reload cog file, same as doing unload then load, do -refresh "name of cog file" or -rf all
    only admin should be able to run this
    param: ctx - The context in which the command has been executed
    param: extension - The name of the Cog file to reload
    """
    if extension == 'all':
        # unload, rest for 2 seconds, then load
        unload_Cogs()
        time.sleep(2)
        load_Cogs()
        await ctx.send('```Success reloading all cogs```')
    else:
        try:
            print(f'> Reloading {extension}.py --')

            await bot.reload_extension(f'cogs.{extension}')

            print(f'> -- {extension}.py reloaded.')
            await ctx.send(f'```Cog {extension}.py reloaded```')
        except commands.ExtensionNotFound:
            await ctx.send(f'```Cog {extension}.py not in directory```')
        except Exception as e:
            await ctx.send(f'```Cog {extension}.py could not be reloaded\n{e}```')

asyncio.run(main())
