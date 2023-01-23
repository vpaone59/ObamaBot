import random
import asyncio
from discord.ext import commands


class game(commands.Cog):
    # game commands for discord bot

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def roll(self, ctx):
        # randomly rolls between 1 and 10,000, for fun!
        roll = random.randint(1, 10000)
        await ctx.send(f'{ctx.message.author.name} rolled {roll}')

    @commands.command(aliases=['duel'])
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def numberduel(self, ctx):
        # number roll 1v1 game

        user1 = ctx.message.author.name
        user2 = ctx.message.mentions[0].name

        # await ctx.send(f'{user1} would like to duel {user2}! Do you accept? (Reply yes/no)')

        # def check(reply):
        #     return reply.content == 'yes'

        # try:
        #     reply = await self.client.wait_for('message', timeout=5.0, check=check)
        # except asyncio.TimeoutError:
        #     await ctx.channel.send(f'ERROR: Timeout Exception, {user1} wins by default.')
        # else:

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
