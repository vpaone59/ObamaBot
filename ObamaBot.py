import discord
from discord.ext import commands
from discord.utils import get
import json
import os
import re
#import schedule
#import time

# search for the json file and load the file
if os.path.exists(os.getcwd() + "/config.json"):
    with open("./config.json") as f:
        configData = json.load(f)

# if the file doesn't exist use the template to create the file
else:
    configTemplate = {"Token": "", "bannedWords": []}

    with open(os.getcwd() + "/config.json", "w+") as f:
        json.dump(configTemplate, f)

TOKEN = configData["TOKEN"]
bannedWords = configData["bannedWords"]
prefix = configData["Prefix"]
obot = discord.Client()
obot = commands.Bot(command_prefix=prefix)


@ obot.event
# wait for the bot to FULLY connect to the server
# once bot connects print message in local terminal
async def on_ready():
    print('We have logged in as {0.user}'.format(obot))


@obot.command()
# https://discordpy.readthedocs.io/en/stable/ext/commands/commands.html
async def hello(ctx):
    user_id = ctx.author
    await ctx.send(f'Hello {user_id.mention}')


@obot.command()
async def goodmorning(ctx):
    await ctx.send(f'Goodmorning my fellow Americans!')
    await ctx.send(file=discord.File(r'gifs\whatever-shrug.gif'))


# @obot.command()
# # create a timer that sends a message every 2 seconds
# # tries to run command, if fail it dumps error to discord channel
# async def starttimer(ctx):
#     try:
#         raise Exception(schedule.every(2).seconds.do(await ctx.send("PENIS")))
#     except Exception as x:
#         await ctx.send({x})

#     while True:
#         schedule.run_pending()
#         time.sleep(1)


@obot.command()
# add a banned word to the bannedWords list in the json config
async def banword(ctx, word):
    if word.lower() in bannedWords:
        await ctx.send("Already banned")
    else:
        bannedWords.append(word.lower())

        with open("./config.json", "r+") as f:
            data = json.load(f)
            data["bannedWords"] = bannedWords
            f.seek(0)
            f.write(json.dumps(data))
            f.truncate()

        # await ctx.message.delete()
        await ctx.send("Word added to banned words list")


@obot.command()
# remove a banned word from the bannedWords list in the json config
async def rmvbannedword(ctx, word):
    if word.lower() in bannedWords:
        bannedWords.remove(word.lower())

        with open("./config.json", "r+") as f:
            data = json.load(f)
            data["bannedWords"] = bannedWords
            f.seek(0)
            f.write(json.dumps(data))
            f.truncate()

        # await ctx.message.delete()
        await ctx.send("Word removed from banned words list")
    else:
        await ctx.send("Word isn't banned")


def msg_contain_word(msg, word):
    # return true if there is a banned word in the message
    # but will not remove attached characters i.e. will remove 'Tom' not 'Tommas'
    return re.search(fr'\b({word})\b', msg) is not None


@obot.event
# respond to certain instances of messages any user may send
async def on_message(message):

    messageAuthor = message.author
    # cleaned up username without # id
    username = str(message.author).split('#')[0]

    user_message = str(message.content)
    channel = str(message.channel.name)
    print(f'{username}: {user_message} ({channel})')

    # ensures the message sent did not contain a banned word
    if bannedWords != None:
        for bannedWord in bannedWords:
            if msg_contain_word(message.content.lower(), bannedWord):
                await message.delete()
                await message.channel.send(f"{messageAuthor.mention} Obama is telling your mother!")

    # prevents bot from replying to itself infinitely
    if message.author == obot.user:
        return

    # .lower() grabs the user message, make the entire message lowercase
    # for easier reading
    if user_message.lower().startswith('hello'):
        await message.channel.send(f'Hello {messageAuthor.mention}!')
        return
    elif 'pooping' in user_message.lower():
        await message.channel.send(f'Obama wishes you a lovely poop!')
        return
    elif 'mud' in user_message.lower():
        await message.channel.send(f'Obama wishes he could shovel some mud with you!')
        return
    elif user_message.lower() == 'thanks obama':
        await message.channel.send(f'You\'re welcome random citizen! \n', file=discord.File(r'gifs\obamacare.jpg'))
        return

    await obot.process_commands(message)


obot.run(TOKEN)
