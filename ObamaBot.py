"""
Vincent Paone
Project began 4/20/2022 --
ObamaBot - main file. Run this file to start the bot.

There is no serious political offiliation. This is all in good fun.
"""

import os # os calls
import re # regex for banned words
import json # for banned words list
import discord # needed
from discord.ext import commands # needed
from dotenv import load_dotenv # to load .env variables
import time

print(f"> STARTING IN {os.getcwd()}")
# load env and assign variables
load_dotenv()
prefix = os.getenv("PREFIX")

# find 'banned.json'
# if it doesn't exist, auto create a new one from template
if os.path.exists('./banned.json'):
    with open("./banned.json") as f:
        bannedWordsData = json.load(f)
else:
    bannedTemplate = {"bannedWords": []}
    with open("./config.json", "w+") as f:
        json.dump(bannedTemplate, f)
# assign current banned words list to variable
bannedWords = bannedWordsData["bannedWords"]

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

    # ensures the message sent did not contain a banned word
    if not user_message.lower().startswith(f"{prefix}unbanword"):
        for word in bannedWords:
            if msg_contain_word(message.content.lower(), word):
                await message.delete()
                await message.channel.send(f"{messageAuthor.mention} banned word detected.")

    # necessary to process the bot's message
    await bot.process_commands(message)



def msg_contain_word(msg, word):
    """
    return true if there is a banned word in the message
    but will not remove attached characters i.e. will remove 'Tom' not 'Tommas'
    \b matches the empty string but only at the beginning or end of the word
    https://docs.python.org/3/library/re.html
    """
    return re.search(fr'.*({word}).*', msg) is not None


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
        await ctx.send(f'Cog {extension}.py unloaded')
    except commands.ExtensionNotLoaded:
        await ctx.send(f'{extension}.py is not loaded')
    except commands.ExtensionNotFound:
        await ctx.send(f'{extension}.py does not exist')


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


@bot.command(aliases=['bw'])
@commands.has_permissions(administrator=True)
async def banword(ctx, word):
    """
    add a banned word to the bannedWords list in the json config
    only admin should be able to run this
    param: ctx - The context of which the command is entered
    param: word - The word you want to be on the banned words list
    """
    if word.lower() in bannedWords:
        # check if the word is already banned
        await ctx.send(f"```{word} is already banned```")
    else:
        bannedWords.append(word.lower())
        # add it to the list
        with open("./config.json", "r+") as f:
            data = json.load(f)
            data["bannedWords"] = bannedWords
            f.seek(0)
            f.write(json.dumps(data))
            f.truncate()  # resizes file

        await ctx.send(f"```{word} added to banned words list```")


@bot.command(aliases=['ubw'])
@commands.has_permissions(administrator=True)
@commands.cooldown(1, 3, commands.BucketType.user)
async def unbanword(ctx, word):
    """
    remove a banned word from the bannedWords list in the json config
    only admin should be able to run this, can only be run 1 time, every 3 seconds, per user
    param: ctx The context of which the command is entered
    param: word - The word you want to remove from the banned words list
    """
    if word.lower() in bannedWords:
        bannedWords.remove(word.lower())

        with open("./config.json", "r+") as f:
            data = json.load(f)
            data["bannedWords"] = bannedWords
            f.seek(0)
            f.write(json.dumps(data))
            f.truncate()

        await ctx.send(f"```{word} removed from banned words list```")

    # if the word isn't in the list
    else:
        await ctx.send(f"```{word} isn't banned```")


@bot.command(aliases=['bl'])
@commands.has_permissions(administrator=True)
@commands.cooldown(1, 5, commands.BucketType.user)
async def banlist(ctx):
    """
    print all of the banned words to the current channel
    only admin should be able to run this, can be run only 1 time, every 5 seconds per user
    param: ctx The context of which the command is entered
    """
    msg = ""
    for w in bannedWords:
        msg = msg + "\n" + w
    await ctx.send(f"```Banned Words:{msg}```")

bot.run(os.getenv("DISCORD_TOKEN"))
