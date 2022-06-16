import discord, asyncio
from discord.ext import commands
from discord.utils import get

# media commands for ObamaBot
# Cogs for Obama Bot
# Cogs are a way to hide standard commands, events, functions etc 
# in another .py file


class media(commands.Cog):

    def __init__(self, client):
        self.client = client

    # do -cry or -c
    @commands.command(aliases=['c'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cry(self, ctx):
        await ctx.send(file=discord.File('gifs/obama-cry.gif'))

    # do -micdrop or md
    @commands.command(aliases=['md'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def micdrop(self, ctx):
        await ctx.send(file=discord.File('gifs/obama-micdrop.gif'))

    # do -micbomb or mb
    @commands.command(aliases=['mb'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def micbomb(self, ctx):
        await ctx.send(file=discord.File('gifs/obama-micbomb.gif'))

    # do -goodmorning or -gm
    @commands.command(aliases=['gm'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def goodmorning(self, ctx):
        await ctx.send(f'Goodmorning my fellow Americans!')
        await ctx.send(file=discord.File('gifs/obama-smile.jpg'))

    # do -goodmorning or -gm
    @commands.command(aliases=['gn'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def goodnight(self, ctx):
        await ctx.send(f'Goodnight and God Bless!')
        await ctx.send(file=discord.File('gifs/obama-sleep.jpeg'))


    # there is a message reply for this as well
    # do -ball or -b
    @commands.command(aliases=['b'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def ball(self, ctx):
        await ctx.send(f'Did someone say...ball?')
        await ctx.send(file=discord.File('gifs/obama-basketball.jpg'))

    # do -thumb or -t
    # reaction must be the same emoji and within 5 seconds
    @commands.command(aliases=['t'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def thumb(self, ctx):
        await ctx.send('React using 🍆 within 5 seconds')

        # checks the author of the reaction and which reaction emoji they used
        def check(user, reaction):
            return user == ctx.message.author and str(reaction.emoji) == '🍆'
         
        # wait 5 seconds to see if the user that ran the command has reacted with the correct emoji
        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=5.0, check=check)
        except asyncio.TimeoutError:
            await ctx.channel.send('ERROR: Timeout Exception')
        else:
            await ctx.channel.send('Obama approves')


    @commands.command(aliases=['monkey'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def monkey_falling(self, ctx):
        await ctx.send(file=discord.File('gifs/monkey-fall.gif'))



def setup(client):
    client.add_cog(media(client))