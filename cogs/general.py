"""
General Commands Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

These are general use commands that any bot should have by default.
"""

from discord.ext import commands


class General(commands.Cog):
    """
    general commands for a Bot
    """

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        """
        runs when Cog is loaded and ready to use
        """
        print(f'{self} ready')

    @commands.command(aliases=['hey', 'hi'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def hello(self, ctx):
        # can be used 1 time, every 2 seconds per user
        await ctx.channel.send(f'Hello {ctx.author.mention}!')

    @commands.command(name='hiall')
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def hello_everyone(self, ctx):
        # can be used 1 time, every 2 seconds per user
        # Bot mentions @'default_role' says Hello
        # This could be the @everyone user depending on the guild
        await ctx.send(f'Hello {ctx.message.guild.default_role}!')

    @commands.command(name='ping', aliases=['p'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def ping(self, ctx):
        # can be used 1 time, every 2 seconds per user
        # Bot gives the current latency
        client_latency = round(self.client.latency * 1000, 2)
        await ctx.send(f'pong {client_latency}ms')

    @commands.command(name='fibonacci', aliases=['fib'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def fib(self, ctx, num):
        # can be used 1 time, every 3 seconds per user
        # Bot calculates Fibonacci sequence
        # param: num - the number sequence to calculate
        n = int(num)
        result = fibonacci(n)
        await ctx.send(f"```Result:\nFibonnaci of {num} = {result}```")


def fibonacci(n):
    # calculate fibonacci sequence for a given n
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


async def setup(client):
    await client.add_cog(General(client))
