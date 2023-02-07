import random
from discord.ext import commands

bee_reacts = ["<:obamagiga:844300314936213565> :point_right: :bee:",
              ":bee: :broom: <:feelsobama:842634906999193620>", "<:obamajoy:842822700912476190> :fire: :bee: :fire:"]

class custom1(commands.Cog):
    """
    custom commands made for a specific discord guild
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['bee', 'b'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def bees(self, ctx):
        # can be used 1 time, every 2 seconds per user
        await ctx.channel.send(random.choice(bee_reacts))

    @commands.command(aliases=['reeve', 'reevez', 'reeves!'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def reeves(self, ctx):
        # can be used 1 time, every 2 seconds per user
        await ctx.channel.send()

def setup(bot):
    bot.add_cog(custom1(bot))
