import discord
import time
import json
import os
from discord.ext import commands
from discord.utils import get
import asyncio

# general commands for any Bot
# Cogs are a way to hide standard commands, events, functions etc in another .py file


class general(commands.Cog):

    def __init__(self, client):
        self.client = client

    # hello command - Bot replies hello and @mentions the user
    # use -hello or -hi

    @commands.command(aliases=['hi'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def hello(self, ctx):
        user_id = ctx.author
        await ctx.send(f'Hello {user_id.mention}')

    # hello all command - Bot @mentions @all users and says hello
    # use -hello0 or -hiall
    @commands.command(aliases=['hiall'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def helloO(self, ctx):
        await ctx.send(f'Hello {ctx.message.guild.default_role}')

    # ping command - Bot replies with the current latency
    # use -ping
    @commands.command(aliases=['p'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def ping(self, ctx):
        client_latency = round(self.client.latency * 1000, 2)
        await ctx.send(f'pong {client_latency}ms')

    # check if the user has the American role. This can be changed to anything
    # param: @user. ex, -rolecheck @user
    @commands.command(aliases=['rolecheck'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def hasRole(self, ctx, user: discord.Member):
        # change 'American' to any role
        role = discord.utils.find(
            lambda r: r.name == 'American', ctx.message.guild.roles)
        if role in user.roles:
            await ctx.send(f"User {user.mention} has the role")
        else:
            await ctx.send(f"User{user.mention} does not have the role")

    # calculate Fibonacci sequence
    # param: num - the number sequence to calculate

    @commands.command()
    async def fib(self, ctx, num):
        # message input comes in as a string, so we cast to int
        n = int(num)
        result = fibonacci(n)
        await ctx.send(f"```Result:\nFibonnaci of {num} = {result}```")


def setup(client):
    client.add_cog(general(client))


# fibonacci function for the fib command
def fibonacci(n):
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

# @commands.command(aliases=['makerole'])
# @commands.cooldown(1, 3, commands.BucketType.user)
# async def createrole(self, ctx, role):
#     if get(ctx.guild.roles, name=role):
#         await ctx.send("Role already exists!")
#     else:
#         await ctx.guild.create_role(name="American", color=discord.Color(0x0062ff))

# @commands.command()
# async def list(self, ctx):
#     # for command in self.client.command:
#     #     await ctx.send(f'{command}')
#     command_list = []
#     all_commands = [command.name for command in self.client.commands]
#     for c in all_commands:
#         command_name = c
#         command_list = command_list + "\n" + command_name
#     if not command_list:
#         await ctx.send(f'no commands available')
#     else:
#         await ctx.send(f'{command_list}')
