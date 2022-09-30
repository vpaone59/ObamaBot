# Vincent Paone
# Project began 4/20/2022 --
# ObamaBot - main file
#
# There is no serious political offiliation. This is all in good fun.

import time
import os
import re
import json
import discord
import asyncio
import requests
from array import array
from ast import alias
from bs4 import BeautifulSoup
from tokenize import String
from discord.ext import commands
from discord.utils import get

# set the current working directory, this is ESSENTIAL to the bot's functionality
current_dir = os.getcwd()
print(current_dir)
print(f"*********** STARTING IN {current_dir} ***********")

if os.path.exists(current_dir + "/config.json"):
    print("***** config path exists *****")
    with open(current_dir + "/config.json") as f:
        print("***** opened config *****")
        configData = json.load(f)

# if the config file doesn't exist within the current directory, use the template to create the file automatically
else:
    print("***** config path DOES NOT exist *****")
    configTemplate = {"Token": "", "Prefix": "", "bannedWords": []}
    with open(current_dir + "/config.json", "w+") as f:
        print("***** new config being created using template *****")
        # dump the configTemplate to the new config.json
        json.dump(configTemplate, f)
        print("***** config created *****")

# grab some info from the config file
TOKEN = configData["TOKEN"]
bannedWords = configData["bannedWords"]
prefix = configData["Prefix"]
# search for the config.json file in the current directory and load the file


# search for the acc.json file in the current directory and load the file
if os.path.exists(current_dir + "/acc.json"):
    print("***** acc path exists *****")
    with open(current_dir + "/acc.json") as f:
        print("***** opened acc *****")
        accData = json.load(f)

# if the acc file doesn't exist use the template to create the file
else:
    print("***** acc path DOES NOT exist *****")
    accTemplate = {"Usernames": [], "Passwords": [], "Account_name": []}
    with open(current_dir + "/acc.json", "w+") as f:
        print("***** new acc being created using template *****")
        # dump the accTemplate to the new acc.json
        json.dump(accTemplate, f)
        print("***** acc created *****")

# grab some info from the acc file
accUsers = accData["Usernames"]
accPasses = accData["Passwords"]
accNick = accData["Account_name"]


# we need to assign the prefix to the bot and denote the bot as 'client'
# 'client' can be called anything it is just a variable to refer to the bot
client = commands.Bot(command_prefix=prefix)

# we need this to check the bot connected properly in the on_ready fxn
full_ready = False


# wait for the bot to FULLY connect to the server
# once bot connects print message in local terminal
@client.event
async def on_ready():
    print(
        'from on_ready: $$$$$ We have logged in as {0.user} $$$$$'.format(client))
    print(f'from on_ready: $$$$$ {client} $$$$$')
    full_ready = True

    if full_ready == True:
        print('from on_ready: $$$$$ Loading Cogs...standby $$$$$')
        loadCogs()
        print('from on_ready: $$$$$ Cogs loaded successfully $$$$$')
    else:
        print('from on_ready: $$$$$ Bot not ready, Cogs not loaded $$$$$')


# every time there is a message in any channel in any guild, this runs
# param: message - The message content that was last sent
@client.event
async def on_message(message):

    # grabs username, user unique id, and the user message
    messageAuthor = message.author
    user_id = str(message.author.id)
    user_message = str(message.content)

    # cleaned up username without # id
    username = str(message.author).split('#')[0]

    # channel name the message was sent from
    channel = str(message.channel.name)
    # server name the message was sent from
    guild = str(message.guild.name)

    # on every message **** in the logs channel **** print it to the terminal
    # print the username, the message, the channel it was sent in and the server (guild)
    # print(f'{username}: {user_message} [userid= {user_id} (channel= {channel})]')
    if channel == 'logs':
        print(f'{username}: {user_message} \t(channel= {channel} on server= {guild})')

    # ignore messages sent from the bot itself
    # prevents infinite replying
    if message.author == client.user:
        return

    # ignore messages sent from other bots
    # prevents infinite replying
    if message.author.bot:
        print(f'last message from bot, returning')
        return

    # ensures the message sent did not contain a banned word
    # allow the message if it starts with command tag -rmvbannedword
    if not user_message.lower().startswith("-rmvbannedword"):
        if bannedWords != None:  # ensure the list isn't empty
            for word in bannedWords:
                if msg_contain_word(message.content.lower(), word):
                    await message.delete()
                    await message.channel.send(f"```{messageAuthor.mention} You used a banned word therefore your message was removed.```")
                    await message.channel.send(f"```{messageAuthor.mention} Obama is telling your Mama! Please do not use banned words!```")

    # if message starts with 'hello'
    if user_message.lower().startswith('hello'):
        await message.channel.send(f'Hello {messageAuthor.mention}!')
        return

    # vinny id 149356710455279617
    # renji id 263560070959333376
    # TO GET IDS RIGHT CLICK A USER'S NAME IN DISCORD AND SELECT COPY ID
    # if the word 'mud' is in any message the specific user sends
    elif 'poop' in user_message.lower() and user_id == '263560070959333376':
        await message.channel.send(f'Thank you for keeping the planet clean! {messageAuthor.mention}')
        return

    # if 'thanks obama' is in the message
    elif 'thanks obama' in user_message.lower():
        await message.channel.send(f'You\'re welcome random citizen! \n', file=discord.File('gifs/obama-smile.jpg'))
        return

    # if the message is exactly 'obama'
    elif user_message.lower() == 'obama':
        # this is just another way to do the message sending with pictures/gifs
        image = discord.File('gifs/obama-wave.jpg')
        image_name = image.filename
        await message.channel.send(file=image)
        # print(f'{username}: {image_name} userid= {user_id} (channel= {channel})')
        return

    # if 'ball' is in the message
    elif 'ball' in user_message.lower():
        await message.channel.send(f'```Did someone say...ball?```', file=discord.File('gifs/obama-basketball.jpg'))
        return

    # if the message starts with the string 'idk'
    elif user_message.lower().startswith('idk'):
        await message.channel.send(file=discord.File('gifs/obama-shrug.gif'))
        return

    # if the message starts with the words 'who asked'
    elif user_message.lower().startswith('who asked'):
        await message.channel.send(file=discord.File('gifs/obama-shrug.gif'))
        return

    # if the word 'horny' is in the message
    elif 'horny' in user_message.lower():
        await message.channel.send(file=discord.File('gifs/obama-lip_bite.jpg'))
        return

    # necessary to process the bot's message
    await client.process_commands(message)


# return true if there is a banned word in the message
# but will not remove attached characters i.e. will remove 'Tom' not 'Tommas'
# \b matches the empty string but only at the beginning or end of the word
# https://docs.python.org/3/library/re.html
def msg_contain_word(msg, word):
    return re.search(fr'\b({word})\b', msg) is not None


# Function to load all Cogs that live in the cogs folder
# Ran on Bot startup
def loadCogs():
    for filename in os.listdir(current_dir + '/cogs'):
        if filename.endswith('.py'):
            try:
                # -3 cuts the .py extension from filename
                client.load_extension(f'cogs.{filename[:-3]}')
                print(f'----- Cog {filename} loaded -----')
            except commands.ExtensionAlreadyLoaded:
                print(f'----- Cog {filename} aleady loaded -----')


# Function to unload all Cogs in the cogs folder
# Runs on -rl all
def unloadCogs():
    for filename in os.listdir(current_dir + '/cogs'):
        if filename.endswith('.py'):
            try:
                client.unload_extension(f'cogs.{filename[:-3]}')
                print(f'----- Cog {filename} unloaded successfully -----')
            except commands.ExtensionNotLoaded:
                print(f'----- Cog {filename} is not loaded -----')


# Load a Cog file
# do -load "name of cog file"
# only admin should be able to run this
# param: ctx - The context in which the command has been executed
# param: extension - The name of the Cog file you want to load
@client.command()
@commands.has_permissions(administrator=True)
async def load(ctx, extension):
    try:
        client.load_extension(f'cogs.{extension}')
        await ctx.send(f'```Cog {extension}.py loaded```')
    except commands.ExtensionAlreadyLoaded:
        await ctx.send(f'```{extension}.py is already loaded```')
    except commands.ExtensionNotFound:
        await ctx.send(f'```{extension}.py does not exist```')


# Unload a Cog file
# do -unload "name of cog file"
# only admin should be able to run this
# param: ctx- The context of which the command is entered
# param: extension - The name of the Cog file to unload
@client.command()
@commands.has_permissions(administrator=True)
async def unload(ctx, extension):
    try:
        client.unload_extension(f'cogs.{extension}')
        await ctx.send(f'Cog {extension}.py unloaded')
    except commands.ExtensionNotLoaded:
        await ctx.send(f'{extension}.py is not loaded')
    except commands.ExtensionNotFound:
        await ctx.send(f'{extension}.py does not exist')


# does unload then load of cog file
# do -rl or -refreshload "name of cog file"
# only admin should be able to run this
# param: ctx - The context in which the command has been executed
# param: extension - The name of the Cog file to reload
# do -rl all to unload/load all Cogs
@client.command(aliases=['rl'], description='Reloads all Cog files')
@commands.has_permissions(administrator=True)
async def refreshload(ctx, extension):

    if extension == 'all':
        unloadCogs()
        await ctx.send(f'``` All Cogs unloaded successfully```')
        time.sleep(2)
        loadCogs()
        await ctx.send(f'``` All Cogs loaded successfully```')
    else:
        try:
            client.unload_extension(f'cogs.{extension}')
            await ctx.send(f'```Cog {extension}.py unloaded```')
            time.sleep(2)
            client.load_extension(f'cogs.{extension}')
            await ctx.send(f'```Cog {extension}.py loaded```')
        except commands.ExtensionNotLoaded:
            client.load_extension(f'cogs.{extension}')
            await ctx.send(f'```Cog {extension}.py loaded```')
        except commands.ExtensionNotFound:
            await ctx.send(f'```Cog {extension}.py not in directory```')


# add a banned word to the bannedWords list in the json config
# only admin should be able to run this
# param: ctx - The context of which the command is entered
# param: word - The word you want to be on the banned words list
@client.command()
@commands.has_permissions(administrator=True)
# message can only be sent 1 time, every 3 seconds, per user.
@commands.cooldown(1, 3, commands.BucketType.user)
async def banword(ctx, word):
    # check if the word is already banned
    if word.lower() in bannedWords:
        await ctx.send("```Already banned```")
    else:
        bannedWords.append(word.lower())
        # add it to the list
        with open("./config.json", "r+") as f:
            data = json.load(f)
            data["bannedWords"] = bannedWords
            f.seek(0)
            f.write(json.dumps(data))
            f.truncate()  # resizes file

        await ctx.send("```Word added to banned words list```")


# remove a banned word from the bannedWords list in the json config
# only admin should be able to run this
# param: ctx The context of which the command is entered
# param: word - The word you want to remove from the banned words list
@client.command(aliases=['unban'])
@commands.has_permissions(administrator=True)
# message can only be sent 1 time, every 3 seconds, per user.
@commands.cooldown(1, 3, commands.BucketType.user)
async def rmvbannedword(ctx, word):
    if word.lower() in bannedWords:
        bannedWords.remove(word.lower())

        with open("./config.json", "r+") as f:
            data = json.load(f)
            data["bannedWords"] = bannedWords
            f.seek(0)
            f.write(json.dumps(data))
            f.truncate()

        await ctx.send("```Word removed from banned words list```")

    # if the word isn't in the list
    else:
        await ctx.send("```Word isn't banned```")


# save information, username/password/nickname into a json
# only admin should be able to run this
# param: ctx The context of which the command is entered
@client.command(aliases=['new_acc'])
@commands.has_permissions(administrator=True)
@commands.cooldown(1, 3, commands.BucketType.user)
async def saveAccount(ctx):

    # prompt #1 for username entry
    await ctx.send(f"Enter in the Username you wish to add {ctx.author.mention}")
    try:
        user_message = await client.wait_for('message', timeout=15, check=lambda message: message.author == ctx.author)
        username = str(user_message.content)
    except asyncio.TimeoutError:
        await ctx.channel.send("```ERROR: Timeout Exception```")

    # prompt #2 for password entry
    await ctx.send(f"Enter in the Password you wish to add {ctx.author.mention}")
    try:
        user_message = await client.wait_for('message', timeout=15, check=lambda message: message.author == ctx.author)
        password = str(user_message.content)
    except asyncio.TimeoutError:
        await ctx.channel.send("```ERROR: Timeout Exception```")

    # check if the account info is already in the list
    if username.lower() in accUsers and password in accPasses:
        userindex = accUsers.index(username)
        passindex = accPasses.index(password)

        if userindex == passindex:
            await ctx.send(f"```Account info already exists at position indices {userindex} and {passindex}\n It will not be appended.```")
    else:
        # add it to the list
        accUsers.append(username.lower())
        accPasses.append(password)
        with open("./acc.json", "r+") as f:
            data = json.load(f)
            data["Usernames"] = accUsers
            data["Passwords"] = accPasses
            f.seek(0)
            f.write(json.dumps(data))
            f.truncate()  # resizes file

    # prompt #3 for nickname entry
    await ctx.send(f"```Provide a nickname for this entry? Reply Y/N```")
    user_message = await client.wait_for('message', timeout=15, check=lambda message: message.author == ctx.author)
    user_reply = str(user_message.content)

    if user_reply.lower() == "y":
        await ctx.send("What would you like to name this entry?")
        user_message = await client.wait_for('message', timeout=15, check=lambda message: message.author == ctx.author)
        nickname = str(user_message.content)

        if nickname.lower() in accNick:
            await ctx.send("Nickname already exists in the list, default will be applied")
            # have them try again, and enter Default for a default nickname to apply
    else:
        # if user does not want to apply a nickname a default will be chosen
        await ctx.send("```No nickname chosen. Default will be applied.```")
        nickname = username + '#' + str(accUsers.index(username))

    accNick.append(nickname)
    with open("./acc.json", "r+") as f:
        data = json.load(f)
        data["Account_name"] = accNick
        f.seek(0)
        f.write(json.dumps(data))
        f.truncate()  # resizes file

    await ctx.send(f"```Added the following account information:\n Username: {username}\n Password: {password}\n Nickname: {nickname}```")


# clear all data from a json file the user chooses
# only admin should be able to run this
# param: ctx The context of which the command is entered
# param: data_file The json file which the user wants wiped of data
@client.command(aliases=['clean'])
@commands.has_permissions(administrator=True)
# message can only be sent 1 time, every 5 seconds, per user.
@commands.cooldown(1, 5, commands.BucketType.user)
async def cleardata(ctx, data_file):

    data_file = "/" + data_file + ".json"
    print(data_file)

    if os.path.exists(current_dir + data_file):
        print("true")
        with open("." + data_file, "r") as f:
            data = json.load(f)
            for o in data:
                data.pop(o)
                await ctx.send(f"Removed {o}")
                print("true")

            f.seek(0)
            f.write(json.dumps(data))
            f.truncate()

    else:
        print("false")


client.run(TOKEN)
