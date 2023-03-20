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
        print(f'{self} ready')

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        whenever a message is sent this Cog will listen and execute code below
        """
        messageAuthor = message.author

        # return whenever a prefix / command message is detected
        if message.startswith(f'{os.getenv("PREFIX")}'):
            return
        # if Walter sends a message the bot will always send the picture below
        if messageAuthor.id == 247936308733935616:
            await message.channel.send(file=discord.File('gifs/weird/boner_alert.jpg'))

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


async def setup(bot):
    await bot.add_cog(Custom1(bot))
