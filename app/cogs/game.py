"""
Game Cog for ObamaBot by Vincent Paone https://github.com/vpaone59
"""

import asyncio
import random

import discord
from discord.ext import commands
from logging_config import create_new_logger

logger = create_new_logger(__name__)


class Game(commands.Cog):
    """
    game commands for a discord bot
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Runs when the cog is loaded
        """
        logger.info("%s ready", self.__cog_name__)

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
    async def numberduel(self, ctx: commands.Context):
        """
        Start a number duel between the command user and a mentioned user.
        Both users roll dice and the higher number wins.

        Usage: !numberduel @user
        """
        try:
            # Validate that a user was mentioned
            if not ctx.message.mentions:
                await ctx.send(
                    "🎲 **Number Duel**: Please mention a user to duel with!\nUsage: `!numberduel @user`"
                )
                return

            if len(ctx.message.mentions) > 1:
                await ctx.send(
                    "🎲 **Number Duel**: Please mention only one user to duel with!"
                )
                return

            user1 = ctx.author
            user2 = ctx.message.mentions[0]

            # Prevent self-dueling
            if user1.id == user2.id:
                await ctx.send(
                    "🎲 **Number Duel**: You can't duel yourself! Mention someone else."
                )
                return

            # Prevent dueling bots
            if user2.bot:
                await ctx.send("🎲 **Number Duel**: You can't duel a bot!")
                return

            logger.info("Number duel started between %s and %s", user1, user2)

            # Roll dice for both users
            user1_roll = random.randint(1, 100)
            user2_roll = random.randint(1, 100)
            roll_diff = abs(user1_roll - user2_roll)

            # Create embed for better presentation
            embed = discord.Embed(title="🎲 Number Duel Results", color=0x00FF00)
            embed.add_field(
                name=f"{user1.display_name}", value=f"🎲 {user1_roll}", inline=True
            )
            embed.add_field(name="VS", value="⚔️", inline=True)
            embed.add_field(
                name=f"{user2.display_name}", value=f"🎲 {user2_roll}", inline=True
            )

            # Determine winner
            if user1_roll > user2_roll:
                embed.add_field(
                    name="🏆 Winner",
                    value=f"{user1.display_name} wins by {roll_diff}!",
                    inline=False,
                )
                embed.color = 0xFFD700  # Gold
            elif user2_roll > user1_roll:
                embed.add_field(
                    name="🏆 Winner",
                    value=f"{user2.display_name} wins by {roll_diff}!",
                    inline=False,
                )
                embed.color = 0xFFD700  # Gold
            else:
                embed.add_field(
                    name="🤝 Result",
                    value="It's a tie! Both rolled the same number!",
                    inline=False,
                )
                embed.color = 0x808080  # Gray

            await ctx.send(embed=embed)
            logger.info(
                "Duel completed: %s (%d) vs %s (%d)",
                user1,
                user1_roll,
                user2,
                user2_roll,
            )

        except IndexError:
            await ctx.send(
                "🎲 **Number Duel**: Please mention a user to duel with!\nUsage: `!numberduel @user`"
            )
        except Exception as e:
            logger.error("Error in numberduel command: %s", e, exc_info=True)
            await ctx.send("❌ An error occurred during the duel. Please try again.")

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
