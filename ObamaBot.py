"""
Vincent Paone
Project began 4/20/2022 --
ObamaBot - main file. Run this file to start the bot.

There is no serious political offiliation. This is all in good fun.
"""

import os # os calls
import discord # needed
from discord.ext import commands # needed
from dotenv import load_dotenv # to load .env variables
import time

print(f"> STARTING IN {os.getcwd()}")
# load env and assign variables
load_dotenv()
prefix = os.getenv("PREFIX")

# initialize the bot with its prefix and intents
intents = discord.Intents.default()
# intents.message_content = True
bot = commands.Bot(command_prefix=prefix, intents=intents)

@bot.event
async def on_ready():
    """
    runs once the bot is fully connected with Discord
    https://discordpy.readthedocs.io/en/stable/api.html?highlight=on_ready#discord.on_ready
    bot logs in then tries to load any cogs in ./cogs
    """
    print(f'> === Logged in as {bot.user} ===')
    try:
        print('> +++ Loading Cogs...standby +++')
        loadCogs()
        print('> +++ Cogs loaded successfully +++')
    except:
        print('> +++ Bot not ready, Cogs not loaded +++')


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

    messageAuthor = message.author
    user_message = str(message.content)

    # necessary to process the bot's message
    await bot.process_commands(message)

def loadCogs():
    """
    Function to load all Cogs that live in the cogs folder
    Ran on Bot startup
    """
    for filename in os.listdir(os.getcwd() + '/cogs'):
        if filename.endswith('.py'):
            try:
                # -3 cuts the .py extension from filename
                bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'>\tCog {filename} loaded\t<')
            except commands.ExtensionAlreadyLoaded:
                print(f'>\tCog {filename} aleady loaded\t<')
            except:
                print(f'>\tCog {filename} NOT loaded\t<')


def unloadCogs():
    """
    Function to unload all Cogs in the cogs folder
    Runs on -rl all
    """
    for filename in os.listdir(os.getcwd() + '/cogs'):
        if filename.endswith('.py'):
            try:
                bot.unload_extension(f'cogs.{filename[:-3]}')
                print(f'>\tCog {filename} unloaded successfully\t<')
            except commands.ExtensionNotLoaded:
                print(f'>\tCog {filename} is not loaded\t<')


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
        bot.load_extension(f'cogs.{extension}')
        ctx.send(f'```Cog {extension}.py loaded```')
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
        bot.unload_extension(f'cogs.{extension}')
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
        unloadCogs()
        time.sleep(2)
        loadCogs()
        await ctx.send('```Success reloading all cogs```')
    else:
        try:
            print(f'> Reloading {extension}.py --')
            
            bot.reload_extension(f'cogs.{extension}')
            
            print(f'> -- {extension}.py reloaded.')
            await ctx.send(f'```Cog {extension}.py reloaded```')
        except commands.ExtensionNotFound:
            await ctx.send(f'```Cog {extension}.py not in directory```')
        except:
            await ctx.send(f'```Cog {extension}.py could not be reloaded```')

bot.run(os.getenv("DISCORD_TOKEN"))
