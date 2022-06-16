from ast import alias
import discord
from discord.ext import commands
from discord.utils import get
import json
import os
import re
import time

from ObamaBot import on_message

# obogs - Obama Cogs
# Cogs for Obama Bot
# Cogs are a way to hide standard commands, events, functions etc 
# in another .py file


class general(commands.Cog):

    def __init__(self, client):
        self.client = client
        

    # do -list
    # list out all currently available commands
    # alternatively -help
    @commands.command()
    async def list(self, ctx):
        # for command in self.client.command:
        #     await ctx.send(f'{command}')
        command_list = []
        all_commands = [command.name for command in self.client.commands]
        for c in all_commands:
            command_name = c
            command_list = command_list + "\n" + command_name
        if not command_list:
            await ctx.send(f'no commands available')
        else:
            await ctx.send(f'{command_list}')

    # do -hi or -hello
    @commands.command(aliases=['hi'])
    # message can only be sent 1 time, every 3 seconds, per user.
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def hello(self, ctx):
        user_id = ctx.author
        await ctx.send(f'Hello {user_id.mention}')

    # do -ping
    @commands.command()
    # message can only be sent 1 time, every 3 seconds, per user.
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def ping(self, ctx):
        client_latency = self.client.latency
        await ctx.send(f'ObamaPong! {client_latency * 1000}ms')

        if client_latency > 1:
            await ctx.send('Wow! You\'re slower than Donald!')
        else:
            time.sleep(1)
            await ctx.send('Get a load of this guy!')

    # do-gm or -goodmorning
    @commands.command(aliases=['gm'])
    # message can only be sent 1 time, every 3 seconds, per user.
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def goodmorning(self, ctx):
        await ctx.send(f'Goodmorning my fellow Americans!')
        await ctx.send(file=discord.File('gifs/obama-smile.jpg'))

    # do -makerole or -createrole
    @commands.command(aliases=['makerole'])
    # message can only be sent 1 time, every 3 seconds, per user.
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def createrole(self, ctx, role):
        if get(ctx.guild.roles, name=role):
            await ctx.send("Role already exists!")
        else:
            await ctx.guild.create_role(name="American", color=discord.Color(0x0062ff))    

    # do -c or -cry
    @commands.command(aliases=['c'])
    # message can only be sent 1 time, every 3 seconds, per user.
    @commands.cooldown(1,3,commands.BucketType.user)
    async def cry(self, ctx):
        await ctx.send(file=discord.File('gifs/obama-cry.gif'))

    # do -md or -micdrop
    @commands.command(aliases=['md'])
    # message can only be sent 1 time, every 3 seconds, per user.
    @commands.cooldown(1,3,commands.BucketType.user)
    async def micdrop(self, ctx):
        await ctx.send(file=discord.File('gifs/obama-micdrop.gif'))

    # do -mb or -micbomb
    @commands.command(aliases=['mb'])
    # message can only be sent 1 time, every 3 seconds, per user.
    @commands.cooldown(1,3,commands.BucketType.user)
    async def micbomb(self, ctx):
        await ctx.send(file=discord.File('gifs/obama-micbomb.gif'))

    # @commands.command(aliases=['f'])
    # @commands.cooldown(1,3,commands.BucketType.user)
    # async def fight(self, ctx):
    #     if on_message()


def setup(client):
    client.add_cog(general(client))

