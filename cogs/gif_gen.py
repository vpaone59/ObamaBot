"""
Gif Generator Cog for ObamaBot by Vincent Paone https://github.com/vpaone59
"""
import random
import os
import json
import random
from urllib import parse, request
from discord.ext import commands

# grab giphy key & assign url to variable
giphy_key = os.getenv("GIPHY_KEY")
url = "http://api.giphy.com/v1/gifs/search"


class Gif_gen(commands.Cog):
    """
    giphy api - gif generator via query
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        runs when Cog is loaded and ready to use
        """
        print(f'{self} ready')

    @commands.command(aliases=['gq', 'gif', 'giphy'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def giphyquery(self, ctx, *query):
        # uses giphy api to search for gifs using user input query strings
        # picks 10 gifs and then randomly chooses 1 to send
        params = parse.urlencode({
            "q": query,
            "api_key": giphy_key,
            "limit": "10"
        })

        with request.urlopen("".join((url, "?", params))) as response:
            data = json.loads(response.read())

        selection = random.randint(0, 9)
        link = data["data"][selection]["embed_url"]
        await ctx.send(f'{link}')


async def setup(bot):
    await bot.add_cog(Gif_gen(bot))
