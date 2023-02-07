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


def setup(client):
    client.add_cog(game(client))
