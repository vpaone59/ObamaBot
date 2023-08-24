"""
Ban Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

THIS FILE MIGHT FAIL THE FIRST TIME THE BOT IS RAN DEPENDING ON 
IF banned.json EXISTS IN THE SAME DIRECTORY AS THE main.py
"""

import json
import os
import re
from discord.ext import commands

# find 'banned.json'
# if it doesn't exist, auto create a new one from template
if os.path.exists("./banned.json"):
    with open("./banned.json") as f:
        bannedWordsData = json.load(f)
else:
    bannedTemplate = {"bannedWords": []}
    with open("./banned.json", "w+") as f:
        json.dump(bannedTemplate, f)
# assign current banned words list to variable for use later
bannedWords = bannedWordsData["bannedWords"]


class Ban(commands.Cog):
    """
    banned words list management commands
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        runs when Cog is loaded and ready to use
        """
        print(f"{self} ready")

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        listens for an on_message call and compares the message to the banned words list using the msg_contain_word fxn
        if a banned word is detected it is removed and the bot replies with a warning
        """
        # convert the incoming message object into a lowercase string so its usable
        msg = str(message.content.lower())
        if msg.startswith(f'{os.getenv("PREFIX")}'):
            return  # command was probably used so we return
        else:
            for word in bannedWords:
                if msg_contain_word(msg, word):
                    await message.channel.send(
                        "```Banned word detected. Please do not use banned words.```"
                    )

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def banword(self, ctx, word):
        """
        add a banned word to the bannedWords list json
        only admin should be able to run this
        param: word - The word you want to be on the banned words list
        """
        print(f"{word}")
        if word.lower() in bannedWords:
            # check if the word is already banned
            await ctx.send(f"```{word} is already banned```")
        else:
            bannedWords.append(word.lower())
            # add it to the list
            with open("./banned.json", "r+") as f:
                data = json.load(f)
                data["bannedWords"] = bannedWords
                f.seek(0)
                f.write(json.dumps(data))
                f.truncate()  # resizes yefile

            await ctx.send(f"```{word} added to banned words list```")

    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def unbanword(self, ctx, word):
        """
        remove a banned word from the bannedWords list json
        only admin should be able to run this, can only be run 1 time, every 3 seconds, per user
        param: word - The word you want to remove from the banned words list
        """
        if word.lower() in bannedWords:
            bannedWords.remove(word.lower())

            with open("./banned.json", "r+") as f:
                data = json.load(f)
                data["bannedWords"] = bannedWords
                f.seek(0)
                f.write(json.dumps(data))
                f.truncate()

            await ctx.send(f"```{word} removed from banned words list```")

        # if the word isn't in the list
        else:
            await ctx.send(f"```{word} isn't banned```")

    @commands.command(aliases=["bl"])
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def banlist(self, ctx):
        """
        print all of the banned words to the current channel
        only admin should be able to run this, can be run only 1 time, every 5 seconds per user
        """
        msg = ""
        for w in bannedWords:
            msg = msg + "\n" + w
        await ctx.send(f"```Banned Words:{msg}```")


def msg_contain_word(msg, word):
    """
    return true if there is a banned word in the message
    """
    return re.search(rf".*({word}).*", msg) is not None


async def setup(bot):
    await bot.add_cog(Ban(bot))
