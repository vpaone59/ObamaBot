from ast import alias
import discord
from discord.ext import commands
from discord.utils import get
import json
import os
import re
import time

# obogs - Obama Cogs
# Cogs for Obama Bot
# Cogs are a way to hide standard commands, events, functions etc 
# in another .py file


class oBogs(commands.Cog):

    def __init__(self, client):
        self.client = client
        


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


    @commands.command(aliases=['hi'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def hello(self, ctx):
        user_id = ctx.author
        await ctx.send(f'Hello {user_id.mention}')

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def ping(self, ctx):
        client_latency = self.client.latency
        await ctx.send(f'ObamaPong! {client_latency}ms')

        if client_latency > 1:
            await ctx.send('Wow! You\'re slower than Donald!')
        else:
            time.sleep(1)
            await ctx.send('Get a load of this guy!')

    @commands.command(aliases=['gm'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def goodmorning(self, ctx):
        await ctx.send(f'Goodmorning my fellow Americans!')
        await ctx.send(file=discord.File('gifs/obama-smile.jpg'))


    @commands.command(aliases=['makerole'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def createrole(self, ctx, role):
        if get(ctx.guild.roles, name=role):
            await ctx.send("Role already exists!")
        else:
            await ctx.guild.create_role(name="American", color=discord.Color(0x0062ff))    


    @commands.command(aliases=['c'])
    @commands.cooldown(1,3,commands.BucketType.user)
    async def cry(self, ctx):
        await ctx.send(file=discord.File('gifs/obama-cry.gif'))


    @commands.command(aliases=['md'])
    @commands.cooldown(1,3,commands.BucketType.user)
    async def micdrop(self, ctx):
            await ctx.send(file=discord.File('gifs/obama-micdrop.gif'))


    @commands.command(aliases=['mb'])
    @commands.cooldown(1,3,commands.BucketType.user)
    async def micbomb(self, ctx):
            await ctx.send(file=discord.File('gifs/obama-micbomb.gif'))



def setup(client):
    client.add_cog(oBogs(client))

