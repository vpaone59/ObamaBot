import discord
from discord.ext import commands
from discord.utils import get

suggestions = []


class general(commands.Cog):
    # general commands for any Bot
    # Cogs are a way to hide standard commands, events, functions etc in another .py file

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['hey', 'hi'])
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def hello(self, ctx):
        await ctx.channel.send(f'Hello {ctx.author.mention}!')

    @commands.command(name='hiall')
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def hello_everyone(self, ctx):
        # hello all command - Bot @mentions @all users and says hello
        # use -hello0 or -hiall
        await ctx.send(f'Hello {ctx.message.guild.default_role}')

    @commands.command(name='ping', aliases=['p'])
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def ping(self, ctx):
        # ping command - Bot replies with the current latency
        # use -ping
        client_latency = round(self.client.latency * 1000, 2)
        await ctx.send(f'pong {client_latency}ms')

    @commands.command(name='fibonacci', aliases=['fib'])
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def fib(self, ctx, num):
        # calculate Fibonacci sequence
        # param: num - the number sequence to calculate
        # input comes in as a string, so we cast to int
        n = int(num)
        result = fibonacci(n)
        await ctx.send(f"```Result:\nFibonnaci of {num} = {result}```")

    @commands.command()
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def suggest(self, ctx, sugs):
        # submit a suggestion for ObamaBot to the developer
        suggestions = []
        suggestions.append(sugs)
        await ctx.send(f'{suggestions}')


def fibonacci(n):
    # fibonacci function for the fib command
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


def setup(client):
    client.add_cog(general(client))
