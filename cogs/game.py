from ast import alias
import asyncio
import discord
from discord.ext import commands
from discord.utils import get
import json
import os
import re
import time

# game commands for ObamaBot
# Cogs for Obama Bot
# Cogs are a way to hide standard commands, events, functions etc 
# in another .py file


class game(commands.Cog):

    def __init__(self, client):
        self.client = client

    # numbers game
    @commands.command(aliases=['duel'])
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def numberduel(self, ctx, user):
        user = str(ctx.message.mentions)

        print(user)
        #def check(message, user):
         #   return message == str(ctx.message.content) and user == ctx.message.author

        # self.client.wait_for('user_versus', 15.0, check=check)


def setup(client):
    client.add_cog(game(client))