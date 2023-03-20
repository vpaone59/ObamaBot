"""
Media Cog for ObamaBot by Vincent Paone https://github.com/vpaone59
"""
import discord
import random
from discord.ext import commands

ball_phrases = ['Did someone say...ball?',
                'Status: Balling.', ':rotating_light: Baller alert :rotating_light:']


class Media(commands.Cog):
    """
    Media cogs/commands for Obama Bot
    These commands will send media to the Guild the command was run in
    """

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        """
        runs when Cog is loaded and ready to use
        """
        print(f'{self} ready')

    @commands.Cog.listener("on_message")
    async def obama_msg(self, message):
        # listens for an on_message hit and then runs the following
        if message.author == self.client.user or message.author.bot:
            return

    @commands.command(aliases=['wed'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def wednesday(self, ctx):
        await ctx.send(file=discord.File('gifs/obama/wednesday.jpg'))

    @commands.command(aliases=['c'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cry(self, ctx):
        await ctx.send(file=discord.File('gifs/obama/obama-cry.gif'))

    @commands.command(aliases=['md'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def micdrop(self, ctx):
        await ctx.send(file=discord.File('gifs/obama/obama-micdrop.gif'))

    @commands.command(aliases=['mb'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def micbomb(self, ctx):
        await ctx.send(file=discord.File('gifs/obama/obama-micbomb.gif'))

    @commands.command(aliases=['gm'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def goodmorning(self, ctx):
        await ctx.send(f'Goodmorning my fellow Americans!', file=discord.File('gifs/obama/obama-smile.jpg'))

    @commands.command(aliases=['gn'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def goodnight(self, ctx):
        await ctx.send(f'Goodnight and God Bless!', file=discord.File('gifs/obama/obama-sleep.jpeg'))

    @commands.command(aliases=['balls'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def ball(self, ctx):
        await ctx.channel.send(random.choice(ball_phrases), file=discord.File('gifs/obama/obama-basketball.jpg'))

    @commands.command(aliases=['monkey', 'm'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def monkey_falling(self, ctx):
        await ctx.send(file=discord.File('gifs/obama/monkey-fall.gif'))

    @commands.command(aliases=['poggers'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def pog(self, ctx):
        await ctx.channel.send("<:obamapog:1040355321102749819>")

    @commands.command(aliases=['thanks'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def thanks_obama(self, ctx):
        await ctx.channel.send(f'You\'re welcome! <:obamacare:844291609663111208>\n', file=discord.File('gifs/obama/obama-smile.jpg'))

    @commands.command(aliases=['obunga'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def obamna(self, ctx):
        await ctx.channel.send("<:obamacare:844291609663111208>")

    @commands.command(aliases=['coord'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def coordinate(self, ctx):
        await ctx.channel.send(":BatChest: :point_up:")

    @commands.command(aliases=['o'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def obama(self, ctx):
        await ctx.channel.send(file=discord.File('gifs/obama/obama-wave.jpg'))

    @commands.command(aliases=['idk'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def i_dont_know(self, ctx):
        await ctx.channel.send("<:obamathink:842635667779616798>")

    @commands.command(aliases=['who', 'whoasked'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def who_asked(self, ctx):
        await ctx.channel.send(file=discord.File('gifs/obama/biden-looking.jpg'))

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def lip_bite(self, ctx):
        await ctx.channel.send(file=discord.File('gifs/obama/obama-lip_bite.jpg'))

    @commands.command(aliases=['smoile'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def wink(self, ctx):
        print("wink")
        await ctx.channel.send(file=discord.File('gifs/obama/obama-wink.gif'))


async def setup(client):
    await client.add_cog(Media(client))
