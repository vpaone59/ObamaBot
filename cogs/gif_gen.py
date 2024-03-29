"""
Gif Generator Cog for ObamaBot by Vincent Paone https://github.com/vpaone59
"""
import random
import os
import json
import random
from urllib import parse, request
from discord.ext import commands
import logging

# grab giphy key & assign url to variable
giphy_key = os.getenv("GIPHY_KEY")
url = "http://api.giphy.com/v1/gifs/search"

logger = logging.getLogger(__name__)


class Gif_gen(commands.Cog):
    """
    giphy api - gif generator via query
    """

    def __init__(self, bot):
        self.bot = bot

        # Configure the logger in the cog to save logs to the file
        file_handler = logging.FileHandler('bot.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)

    @commands.Cog.listener()
    async def on_ready(self):
        """
        runs when Cog is loaded and ready to use
        """
        print(f'{self} ready')

    @commands.command(aliases=['gq', 'gif', 'giphy'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def giphyquery(self, ctx, *query):
        """
        Uses giphy api to search for gifs using user input query strings
        Picks 10 gifs and then randomly chooses 1 to send
        """
        params = parse.urlencode({
            "q": query,
            "api_key": giphy_key,
            "limit": "10"
        })
        try:
            with request.urlopen("".join((url, "?", params))) as response:
                data = json.loads(response.read())
                # if there are no gifs returned we edit the bot's response
                if len(data["data"]) == 0:
                    raise Exception(
                        f"No gifs found for {query}, try again with a different search query")
                else:
                    selection = random.randint(0, 9)
                    link = data["data"][selection]["embed_url"]
                    await ctx.send(f'{link}')
        except Exception as e:
            logger.error(e)
            await ctx.send(f'```{e}```')


async def setup(bot):
    await bot.add_cog(Gif_gen(bot))
