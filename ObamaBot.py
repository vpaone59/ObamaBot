# Vincent Paone
# 4/20/2022 --
# ObamaBot - main file
# 
#

from ast import alias
import discord
from discord.ext import commands
from discord.utils import get
import json
import os
import re
import time


# search for the config.json file and load the file
if os.path.exists(os.getcwd() + "/config.json"):
    with open("./config.json") as f:
        configData = json.load(f)

# if the config file doesn't exist use the template to create the file
else:
    configTemplate = {"Token": "", "Prefix": "", "bannedWords": []}

    with open(os.getcwd() + "/config.json", "w+") as f:
        json.dump(configTemplate, f) # dump the configTemplate to the new config.json


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
# wait for the bot to FULLY connect to the server
# once bot connects print message in local terminal
async def on_ready():
        print('We have logged in as {0.user}'.format(client))
        print(f'[][][] {client} [][][]')
        full_ready = True

        if full_ready == True:
            loadCogs()
        else:
            print('Bot not ready, Cogs not loaded')


# Function to load all Cogs in the cogs folder
# Ran on Bot startup
def loadCogs():
    for filename in os.listdir('./cogs'):
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
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                client.unload_extension(f'cogs.{filename[:-3]}')
                print(f'----- Cog {filename} unloaded successfully -----')
            except commands.ExtensionNotLoaded:
                print(f'----- Cog {filename} is not loaded -----')
            

# return true if there is a banned word in the message
# but will not remove attached characters i.e. will remove 'Tom' not 'Tommas'
# \b matches the empty string but only at the beginning or end of the word
# https://docs.python.org/3/library/re.html        
def msg_contain_word(msg, word):
        return re.search(fr'\b({word})\b', msg) is not None


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
        await ctx.send(f'Cog {extension}.py loaded')
    except commands.ExtensionAlreadyLoaded:
        await ctx.send(f'{extension}.py is already loaded')
    except commands.ExtensionNotFound:
        await ctx.send(f'{extension}.py does not exist')


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
@client.command(aliases= ['rl'], description= 'Reloads all Cog files')
@commands.has_permissions(administrator=True)
async def refreshload(ctx, extension):
    
    if extension == 'all':
        unloadCogs()
        time.sleep(2)
        loadCogs()    
    else:
        try:
            client.unload_extension(f'cogs.{extension}')
            await ctx.send(f'Cog {extension}.py unloaded')
            time.sleep(2)
            client.load_extension(f'cogs.{extension}')
            await ctx.send(f'Cog {extension}.py loaded')
        except commands.ExtensionNotLoaded:
            client.load_extension(f'cogs.{extension}')
            await ctx.send(f'Cog {extension}.py loaded')
        except commands.ExtensionNotFound:
            await ctx.send(f'Cog {extension}.py not in directory')
        

# add a banned word to the bannedWords list in the json config
# only admin should be able to run this
# param: ctx - The context of which the command is entered
# param: word - The word you want to be on the banned words list
@client.command()
@commands.has_permissions(administrator=True)
# message can only be sent 1 time, every 3 seconds, per user.
@commands.cooldown(1, 3, commands.BucketType.user)
async def banword(ctx, word):
    #check if the word is already banned
    if word.lower() in bannedWords:
        await ctx.send("Already banned")
    else:
        bannedWords.append(word.lower())
        #add it to the list
        with open("./config.json", "r+") as f:
            data = json.load(f)
            data["bannedWords"] = bannedWords
            f.seek(0) 
            f.write(json.dumps(data)) 
            f.truncate() #resizes file

        await ctx.send("Word added to banned words list")


# remove a banned word from the bannedWords list in the json config
# only admin should be able to run this
# param: ctx The context of which the command is entered
# param: word - The word you want to remove from the banned words list
@client.command(aliases = ['unban'])
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

        await ctx.send("Word removed from banned words list")

    #if the word isn't in the list    
    else:
        await ctx.send("Word isn't banned")


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

    
    # print the message to the terminal
    # print(f'{username}: {user_message} [userid= {user_id} (channel= {channel})]')
    print(f'{username}: {user_message} \t(channel= {channel} on server= {guild})')
    
    # ignore messages sent from the bot itself
    # prevents infinite replying
    if message.author == client.user:
        return


    # ensures the message sent did not contain a banned word
    # allow the message if it starts with command tag -rmvbannedword
    if not user_message.lower().startswith("-rmvbannedword"):
        if bannedWords != None: # ensure the list isn't empty
            for word in bannedWords:
                if msg_contain_word(message.content.lower(), word): 
                    await message.delete()
                    await message.channel.send(f"{messageAuthor.mention} You used a banned word therefore your message was removed.")
                    await message.channel.send(f"{messageAuthor.mention} Obama is telling your Mama! Please do not use banned words!")

    # some hardcoded messages and replies
    if user_message.lower().startswith('hello'):
        await message.channel.send(f'Hello {messageAuthor.mention}!')
        return

    # reply for specific message and user
    elif 'mud' in user_message.lower() and user_id == '263560070959333376':
        await message.channel.send(f'Thank you for keeping the planet clean! {messageAuthor.mention}')
        return

    elif user_message.lower() == 'thanks obama':
        await message.channel.send(f'You\'re welcome random citizen! \n', file=discord.File('gifs/obama-smile.jpg'))
        return

    elif user_message.lower() == 'obama':
        # this is just another way to do the message sending with pictures/gifs
        image = discord.File('gifs/obama-wave.jpg')
        image_name = image.filename
        await message.channel.send(file=image)
        # print(f'{username}: {image_name} userid= {user_id} (channel= {channel})')
        return

    elif user_message.lower().startswith('ball'):
        await message.channel.send(f'Did someone say...ball?')
        await message.channel.send(file=discord.File('gifs/obama-basketball.jpg'))
        return

    elif user_message.lower().startswith('idk'):
        await message.channel.send(file=discord.File('gifs/obama-shrug.gif'))
        return

    elif user_message.lower().startswith('who asked'):
        await message.channel.send(file=discord.File('gifs/obama-shrug.gif'))
        return
    
    


    
    
    await client.process_commands(message)



client.run(TOKEN)
