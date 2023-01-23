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
from array import array
from ast import alias
from tokenize import String
from discord.ext import commands
from discord.utils import get
from pathlib import Path

# set the current working directory, this is ESSENTIAL to the bot's functionality
current_dir = os.getcwd()
cog_files = []
for f in os.listdir(current_dir + '/cogs'):
    if f.endswith('.py'):
        cog_files.append(f)

print(f"////////// STARTING IN {current_dir}")

if os.path.exists(current_dir + "/config.json"):
    print("////////// config path exists")
    with open(current_dir + "/config.json") as f:
        print("////////// opened config")
        configData = json.load(f)

# if the config file doesn't exist within the current directory, use the template to create the file automatically
else:
    print("////////// config path DOES NOT exist")
    configTemplate = {"Token": "", "Prefix": "", "bannedWords": []}
    with open(current_dir + "/config.json", "w+") as f:
        print("////////// new config being created using template")
        # dump the configTemplate to the new config.json
        json.dump(configTemplate, f)
        print("////////// config created")

# grab some info from the config file
TOKEN = configData["TOKEN"]
bannedWords = configData["bannedWords"]
prefix = configData["Prefix"]

# we need to assign the prefix to the bot and denote the bot as 'client'
# 'client' can be called anything it is just a variable to refer to the bot
client = commands.Bot(command_prefix=prefix)

# we need this to check the bot connected properly in the on_ready fxn
full_ready = False


@client.event
async def on_ready():
    # wait for the bot to FULLY connect to the server
    # once bot connects print message in local terminal
    print(f'////////// We have logged in as {client.user}')
    full_ready = True
    if full_ready == True:
        print('////////// Loading Cogs...standby')
        loadCogs()
        print('////////// Cogs loaded successfully')
    else:
        print('////////// Bot not ready, Cogs not loaded')


@client.event
async def on_message(message):
    # every time there is a message in any channel in any guild, this runs
    # param: message - The message that was last sent to the channel

    # ignore messages sent from the bot itself and other bots
    # prevents infinite replying
    if message.author == client.user or message.author.bot:
        return

    messageAuthor = message.author
    user_message = str(message.content)

    # user_id = str(message.author.id)
    # username = str(message.author).split('#')[0]
    # channel = str(message.channel.name)
    # guild = str(message.guild.name)

    # ensures the message sent did not contain a banned word
    if not user_message.lower().startswith(f"{prefix}unbanword"):
        for word in bannedWords:
            if msg_contain_word(message.content.lower(), word):
                await message.delete()
                await message.channel.send(f"{messageAuthor.mention} You used a banned word therefore your message was removed.")
                await message.channel.send(f"Obama is telling your Mama! Please do not use banned words!")

    # necessary to process the bot's message
    await client.process_commands(message)


# return true if there is a banned word in the message
# but will not remove attached characters i.e. will remove 'Tom' not 'Tommas'
# \b matches the empty string but only at the beginning or end of the word
# https://docs.python.org/3/library/re.html
def msg_contain_word(msg, word):
    return re.search(fr'.*({word}).*', msg) is not None


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


def unloadCogs():
    # Function to unload all Cogs in the cogs folder
    # Runs on -rl all
    for filename in os.listdir(current_dir + '/cogs'):
        if filename.endswith('.py'):
            try:
                client.unload_extension(f'cogs.{filename[:-3]}')
                print(f'----- Cog {filename} unloaded successfully -----')
            except commands.ExtensionNotLoaded:
                print(f'----- Cog {filename} is not loaded -----')


@client.command()
@commands.has_permissions(administrator=True)
async def load(ctx, extension):
    # Load a Cog file
    # do -load "name of cog file"
    # only admin should be able to run this
    # param: ctx - The context in which the command has been executed
    # param: extension - The name of the Cog file you want to load
    try:
        client.load_extension(f'cogs.{extension}')
        await ctx.send(f'```Cog {extension}.py loaded```')
    except commands.ExtensionAlreadyLoaded:
        await ctx.send(f'```{extension}.py is already loaded```')
    except commands.ExtensionNotFound:
        await ctx.send(f'```{extension}.py does not exist```')


@client.command()
@commands.has_permissions(administrator=True)
async def unload(ctx, extension):
    # Unload a Cog file
    # do -unload "name of cog file"
    # only admin should be able to run this
    # param: ctx- The context of which the command is entered
    # param: extension - The name of the Cog file to unload
    try:
        client.unload_extension(f'cogs.{extension}')
        await ctx.send(f'Cog {extension}.py unloaded')
    except commands.ExtensionNotLoaded:
        await ctx.send(f'{extension}.py is not loaded')
    except commands.ExtensionNotFound:
        await ctx.send(f'{extension}.py does not exist')


@client.command(aliases=['rf'], description='Reloads all Cog files')
@commands.has_permissions(administrator=True)
async def refresh(ctx, extension):
    # reload cog file, same as doing unload then load
    # do -rf or -refresh "name of cog file"
    # only admin should be able to run this
    # param: ctx - The context in which the command has been executed
    # param: extension - The name of the Cog file to reload
    # do -rf all to unload/load all Cogs
    if extension == 'all':
        for cog in cog_files:
            await ctx.send(f'{cog} working...')
            client.reload_extension(cog)
            await ctx.send(f'Cog {cog} reloaded')
    else:
        try:
            client.reload_extension(f'cogs.{extension}')
            await ctx.send(f'```Cog {extension}.py reloaded```')
        except commands.ExtensionNotFound:
            await ctx.send(f'```Cog {extension}.py not in directory```')


@client.command(aliases=['bw'])
@commands.has_permissions(administrator=True)
@commands.cooldown(1, 3, commands.BucketType.user)
async def banword(ctx, word):
    # add a banned word to the bannedWords list in the json config
    # only admin should be able to run this
    # param: ctx - The context of which the command is entered
    # param: word - The word you want to be on the banned words list
    # check if the word is already banned
    if word.lower() in bannedWords:
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


@client.command(aliases=['ubw'])
@commands.has_permissions(administrator=True)
@commands.cooldown(1, 3, commands.BucketType.user)
async def unbanword(ctx, word):
    # remove a banned word from the bannedWords list in the json config
    # only admin should be able to run this
    # param: ctx The context of which the command is entered
    # param: word - The word you want to remove from the banned words list
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


@client.command(name='banlist', aliases=['bl'])
@commands.has_permissions(administrator=True)
@commands.cooldown(1, 3, commands.BucketType.user)
async def banlist(ctx):
    # print all of the banned words to the current channel
    # only admin should be able to run this
    # param: ctx The context of which the command is entered
    msg = ""
    for w in bannedWords:
        msg = msg + "\n" + w
    await ctx.send(f"```Banned Words:{msg}```")


# # save information, username/password/nickname into a json
# # only admin should be able to run this
# # param: ctx The context of which the command is entered
# @client.command(aliases=['new_acc'])
# @commands.has_permissions(administrator=True)
# @commands.cooldown(1, 3, commands.BucketType.user)
# async def saveAccount(ctx):

#     # prompt #1 for username entry
#     await ctx.send(f"Enter in the Username you wish to add {ctx.author.mention}")
#     try:
#         user_message = await client.wait_for('message', timeout=15, check=lambda message: message.author == ctx.author)
#         username = str(user_message.content)
#     except asyncio.TimeoutError:
#         await ctx.channel.send("```ERROR: Timeout Exception```")

#     # prompt #2 for password entry
#     await ctx.send(f"Enter in the Password you wish to add {ctx.author.mention}")
#     try:
#         user_message = await client.wait_for('message', timeout=15, check=lambda message: message.author == ctx.author)
#         password = str(user_message.content)
#     except asyncio.TimeoutError:
#         await ctx.channel.send("```ERROR: Timeout Exception```")

#     # check if the account info is already in the list
#     if username.lower() in accUsers and password in accPasses:
#         userindex = accUsers.index(username)
#         passindex = accPasses.index(password)

#         if userindex == passindex:
#             await ctx.send(f"```Account info already exists at position indices {userindex} and {passindex}\n It will not be appended.```")
#     else:
#         # add it to the list
#         accUsers.append(username.lower())
#         accPasses.append(password)
#         with open("./acc.json", "r+") as f:
#             data = json.load(f)
#             data["Usernames"] = accUsers
#             data["Passwords"] = accPasses
#             f.seek(0)
#             f.write(json.dumps(data))
#             f.truncate()  # resizes file

#     # prompt #3 for nickname entry
#     await ctx.send(f"```Provide a nickname for this entry? Reply Y/N```")
#     user_message = await client.wait_for('message', timeout=15, check=lambda message: message.author == ctx.author)
#     user_reply = str(user_message.content)

#     if user_reply.lower() == "y":
#         await ctx.send("What would you like to name this entry?")
#         user_message = await client.wait_for('message', timeout=15, check=lambda message: message.author == ctx.author)
#         nickname = str(user_message.content)

#         if nickname.lower() in accNick:
#             await ctx.send("Nickname already exists in the list, default will be applied")
#             # have them try again, and enter Default for a default nickname to apply
#     else:
#         # if user does not want to apply a nickname a default will be chosen
#         await ctx.send("```No nickname chosen. Default will be applied.```")
#         nickname = username + '#' + str(accUsers.index(username))

#     accNick.append(nickname)
#     with open("./acc.json", "r+") as f:
#         data = json.load(f)
#         data["Account_name"] = accNick
#         f.seek(0)
#         f.write(json.dumps(data))
#         f.truncate()  # resizes file

#     await ctx.send(f"```Added the following account information:\n Username: {username}\n Password: {password}\n Nickname: {nickname}```")


# # clear all data from a json file the user chooses
# # only admin should be able to run this
# # param: ctx The context of which the command is entered
# # param: data_file The json file which the user wants wiped of data
# @client.command(aliases=['clean'])
# @commands.has_permissions(administrator=True)
# # message can only be sent 1 time, every 5 seconds, per user.
# @commands.cooldown(1, 5, commands.BucketType.user)
# async def cleardata(ctx, data_file):

#     data_file = "/" + data_file + ".json"
#     print(data_file)

#     if os.path.exists(current_dir + data_file):
#         print("true")
#         with open("." + data_file, "r") as f:
#             data = json.load(f)
#             for o in data:
#                 data.pop(o)
#                 await ctx.send(f"Removed {o}")
#                 print("true")

#             f.seek(0)
#             f.write(json.dumps(data))
#             f.truncate()

#     else:
#         print("false")


client.run(TOKEN)
