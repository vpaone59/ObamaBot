import asyncio
import random
from discord.ext import commands


class game(commands.Cog):
    """ 
    game commands for a discord bot
    """

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def roll(self, ctx):
        # can be used 1 time, every 2 seconds per user
        # randomly rolls between 1 and 10,000
        roll = random.randint(1, 10000)
        await ctx.send(f'{ctx.message.author.name} rolled {roll}')

    @commands.command(aliases=['duel'])
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def numberduel(self, ctx):
        # can be used 1 time, every 5 seconds per user
        # number roll 1v1 game

        user1 = ctx.message.author.name
        user2 = ctx.message.mentions[0].name

        user1_roll = random.randint(1, 100)
        user2_roll = random.randint(1, 100)
        roll_diff = abs(user1_roll - user2_roll)

        await ctx.send(f'{user1} rolled {user1_roll}\n{user2} rolled {user2_roll}')
        if user1_roll > user2_roll:
            await ctx.send(f'{user1} wins with a difference of {roll_diff}')
        else:
            await ctx.send(f'{user2} wins with a difference of {roll_diff}')

    @commands.command(aliases=['r'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def react(self, ctx):
        # waits for the user to react with the same emoji the Bot used
        
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
        
def setup(client):
    client.add_cog(game(client))
