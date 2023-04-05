"""
General Commands Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

These are general use commands that any bot should have by default.
"""

from discord.ext import commands


class General(commands.Cog):
    """
    general commands for a Bot
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        runs when Cog is loaded and ready to use
        """
        print(f'{self} ready')

    @commands.command(aliases=['hey', 'hi'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def hello(self, ctx):
        """
        Reply mention to the user
        """
        await ctx.channel.send(f'Hello {ctx.author.mention}!')

    @commands.command(name='hiall')
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def hello_everyone(self, ctx):
        """
        Reply mention to all users
        """
        await ctx.send(f'Hello {ctx.message.guild.default_role}!')

    @commands.command(name='ping', aliases=['p'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def ping(self, ctx):
        """
        Send ping to server
        """
        bot_latency = round(self.bot.latency * 1000, 2)
        await ctx.send(f'pong {bot_latency}ms')

    @commands.command(name='fibonacci', aliases=['fib'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def fib(self, ctx, num):
        """
        Calculate fibonacci of the parameter input
        paramter num: number in the fibonacci sequence to calculate
        """
        n = int(num)
        result = fibonacci(n)
        await ctx.send(f"```Result:\nFibonnaci of {num} = {result}```")


def fibonacci(n):
    """
    calculate fibonacci sequence for a given n
    """
    if n < 0:
        print(f"User input {n}: negative not allowed ")
    elif n == 0:
        print(f"User input {n}: Fib({n}) = 0")
        return 0
    elif n == 1 or n == 2:
        print(f"User input {n}: Fib({n}) = 1")
        return 1
    else:
        fib = fibonacci(n-1) + fibonacci(n-2)
        return fib


async def setup(bot):
    await bot.add_cog(General(bot))
