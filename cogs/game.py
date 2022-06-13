import random, asyncio
from discord.ext import commands


# game commands for ObamaBot
# Cogs for Obama Bot
# Cogs are a way to hide standard commands, events, functions etc 
# in another .py file


class game(commands.Cog):

    def __init__(self, client):
        self.client = client

    # numbers game
    @commands.command(aliases=['duel'])
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def numberduel(self, ctx):
        user1 = ctx.message.author
        print(user1)
        user2 = ctx.message.mentions[0].id
        print(user2)

        await ctx.send('{user1} would like to duel {user2}!\n{user2} do you accept? (Reply yes/no)')
        
        try:
            reply, user = await self.client.wait_for('message', timeout=10.0)
        except asyncio.TimeoutError:
            await ctx.channel.send('ERROR: Timeout Exception, {user1} wins by default.')
        else:
            user1_roll = random.randint(1,100)
            user2_roll = random.randint(1,100)
            roll_diff = user1_roll - user2_roll

            await ctx.send('{user1} rolled {user1_roll}\n{user2} rolled {user2_roll}')
            if user1_roll > user2_roll:
                await ctx.send('{user1} wins with a {roll_diff} differential')
            else:
                await ctx.send('{user2} wins with a {roll_diff} differential')
        
        # #def check(message, user):
         #   return message == str(ctx.message.content) and user == ctx.message.author

        # self.client.wait_for('user_versus', 15.0, check=check)


def setup(client):
    client.add_cog(game(client))