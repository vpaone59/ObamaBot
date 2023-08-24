"""
Game Cog for ObamaBot by Vincent Paone https://github.com/vpaone59
"""

import asyncio
import random
from discord.ext import commands


class Game(commands.Cog):
    """
    game commands for a discord bot
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        runs when Cog is loaded and ready to use
        """
        print(f"{self} ready")

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def roll(self, ctx):
        """
        Roll a random int from 1 to 10000
        """
        roll = random.randint(1, 10000)
        await ctx.send(f"{ctx.message.author.name} rolled {roll}")

    @commands.command(aliases=["duel"])
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def numberduel(self, ctx):
        """
        Rolls 2 random ints and compares them
        parameter is @another_user
        """
        user1 = ctx.message.author.name
        user2 = ctx.message.mentions[0].name

        user1_roll = random.randint(1, 100)
        user2_roll = random.randint(1, 100)
        roll_diff = abs(user1_roll - user2_roll)

        await ctx.send(f"{user1} rolled {user1_roll}\n{user2} rolled {user2_roll}")
        if user1_roll > user2_roll:
            await ctx.send(f"{user1} wins with a difference of {roll_diff}")
        else:
            await ctx.send(f"{user2} wins with a difference of {roll_diff}")

    @commands.command(aliases=["r"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def react(self, ctx):
        """
        Waits for the user to react with the same emoji the Bot used
        """

        await ctx.send("React using 🍆 within 5 seconds")
        # checks the author of the reaction and which reaction emoji they used

        def check(reaction, user):
            return user == ctx.message.author and reaction.emoji == "🍆"

        # wait 5 seconds to see if the user that ran the command has reacted with the correct emoji
        try:
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=5.0, check=check
            )
        except asyncio.TimeoutError:
            await ctx.channel.send("ERROR: Timeout Exception")
        else:
            await ctx.channel.send("Obama approves")


async def setup(bot):
    await bot.add_cog(Game(bot))
