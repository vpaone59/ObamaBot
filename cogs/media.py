import discord
import asyncio
import random
from discord.ext import commands
from discord.utils import get
import re

ball_phrases = ['Did someone say...ball?',
                'Status: Balling.', ':rotating_light: Baller alert :rotating_light:']


class media(commands.Cog):
    # Media Cogs/Commands for Obama Bot

    def __init__(self, client):
        self.client = client

    @commands.cooldown(1, 30)
    @commands.Cog.listener("on_message")
    async def obama_msg(self, message):
        if message.author == self.client.user or message.author.bot:
            return

    @commands.command(aliases=['r'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def react(self, ctx):
        await ctx.send('React using 🍆 within 5 seconds')

        # checks the author of the reaction and which reaction emoji they used
        def check(reaction, user):
            return user == ctx.message.author and reaction.emoji == '🍆'

        # wait 5 seconds to see if the user that ran the command has reacted with the correct emoji
        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=5.0, check=check)
        except asyncio.TimeoutError:
            await ctx.channel.send('ERROR: Timeout Exception')
        else:
            await ctx.channel.send('Obama approves')

    @commands.command(aliases=['c'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def cry(self, ctx):
        await ctx.send(file=discord.File('gifs/obama-cry.gif'))

    @commands.command(aliases=['md'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def micdrop(self, ctx):
        await ctx.send(file=discord.File('gifs/obama-micdrop.gif'))

    @commands.command(aliases=['mb'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def micbomb(self, ctx):
        await ctx.send(file=discord.File('gifs/obama-micbomb.gif'))

    @commands.command(aliases=['gm'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def goodmorning(self, ctx):
        await ctx.send(f'Goodmorning my fellow Americans!', file=discord.File('gifs/obama-smile.jpg'))

    @commands.command(aliases=['gn'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def goodnight(self, ctx):
        await ctx.send(f'Goodnight and God Bless!', file=discord.File('gifs/obama-sleep.jpeg'))

    @commands.command(aliases=['balls'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def ball(self, ctx):
        await ctx.channel.send(random.choice(ball_phrases), file=discord.File('gifs/obama-basketball.jpg'))

    @commands.command(aliases=['monkey', 'm'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def monkey_falling(self, ctx):
        await ctx.send(file=discord.File('gifs/monkey-fall.gif'))

    @commands.command(aliases=['poggers'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def pog(self, ctx):
        await ctx.channel.send("<:obamapog:1040355321102749819>")

    @commands.command(aliases=['thanks'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def thanks_obama(self, ctx):
        await ctx.channel.send(f'You\'re welcome! <:obamacare:844291609663111208>\n', file=discord.File('gifs/obama-smile.jpg'))

    @commands.command(aliases=['obunga'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def obamna(self, ctx):
        await ctx.channel.send("<:obamacare:844291609663111208>")

    @commands.command(aliases=['coord'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def coordinate(self, ctx):
        await ctx.channel.send(":BatChest: :point_up:")

    @commands.command(aliases=['o'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def obama(self, ctx):
        await ctx.channel.send(file=discord.File('gifs/obama-wave.jpg'))

    @commands.command(aliases=['idk'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def i_dont_know(self, ctx):
        await ctx.channel.send("<:obamathink:842635667779616798>")

    @commands.command(aliases=['who', 'whoasked'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def who_asked(self, ctx):
        await ctx.channel.send(file=discord.File('gifs/biden-looking.jpg'))

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def lip_bite(self, ctx):
        await ctx.channel.send(file=discord.File('gifs/obama-lip_bite.jpg'))


def setup(client):
    client.add_cog(media(client))
