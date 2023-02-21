import random
from discord.ext import commands

bee_reacts = ["<:obamagiga:844300314936213565> :point_right: :bee:",
              ":bee: :broom: <:feelsobama:842634906999193620>", "<:obamajoy:842822700912476190> :fire: :bee: :fire:"]

class Custom1(commands.Cog):
    """
    custom commands made for a specific discord guild
    """

    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} ready')

    @commands.command(aliases=['bee', 'b'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def bees(self, ctx):
        await ctx.channel.send(random.choice(bee_reacts))

    @commands.command(aliases=['reeve', 'reevez', 'reeves!'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def reeves(self, ctx):
        await ctx.channel.send()

async def setup(bot):
    await bot.add_cog(Custom1(bot))
