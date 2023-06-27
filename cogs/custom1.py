"""
Custom1 Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

This Cog is custom made for a specific server and will not work in normal servers.
"""

import os
import random
import discord
from discord.ext import commands

bee_reacts = ["<:obamagiga:844300314936213565> :point_right: :bee:",
              ":bee: :broom: <:feelsobama:842634906999193620>", "<:obamajoy:842822700912476190> :fire: :bee: :fire:"]


class Custom1(commands.Cog):
    """
    custom commands made for a specific discord guild
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        runs when Cog is loaded and ready to use
        """
        print(f'{self} ready')

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        whenever a message is sent this Cog will listen and execute code below
        """
        messageAuthor = message.author
        string_message = str(message.content)
        # return whenever a prefix / command message is detected
        if string_message.startswith(f'{os.getenv("PREFIX")}'):
            return

        # if DJ is @ mentioned
        for user in message.mentions:
            if user.id == 123107464240562180:
                # if user.id == 965414583860883456: # dog dev user ID
                file_name = get_random_batman_deej_file()
                if file_name:
                    file_path = os.path.join('gifs/memes', file_name)
                    await message.channel.send(file=discord.File(file_path))
                break  # Once the user is found, we can break out of the loop

        # if Walter sends a message the bot will always send the picture below
        if messageAuthor.id == 247936308733935616:
            await message.channel.send(file=discord.File('gifs/weird/boner_alert.jpg'))

        if message.guild.id == 842545435050508328:
            if string_message.startswith("INC"):
                format_link = format_incident_link(string_message)
                await message.channel.send(f'{format_link}')

    @commands.command(aliases=['bee', 'b'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def bees(self, ctx):
        """
        Random reaction for a bees command
        """
        await ctx.channel.send(random.choice(bee_reacts))

    @commands.command(aliases=['reeve', 'reevez', 'reeves!'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def reeves(self, ctx):
        """
        Send a picture of Reeves!
        """
        await ctx.channel.send(file=discord.File('gifs/weird/Reeves/Reeves_gun_permit.jpg'))


def format_incident_link(incident_number):
    """
    Format incident number to a clickable link
    """
    return f"https://s.rowan.edu/{incident_number}"


def get_random_batman_deej_file():
    """
    Get all files in the memes directory that are of .png and contain 'batman_deej' in the filename
    """
    folder_path = 'gifs/memes'
    files = [file for file in os.listdir(folder_path) if file.endswith(
        '.png') and 'batman_deej' in file]
    if files:
        return random.choice(files)
    else:
        return None


async def setup(bot):
    await bot.add_cog(Custom1(bot))
