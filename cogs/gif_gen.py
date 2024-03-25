"""
GIF Generator Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

Utilizes the Giphy API
"""

import random
import os
import json
from logging_config import setup_logging
from urllib import parse, request
from discord.ext import commands

# Grab Giphy key & assign url to variable
giphy_key = os.getenv("GIPHY_KEY")
URL = "http://api.giphy.com/v1/gifs/search"

logger = setup_logging(__name__)


class Gif_Generator(commands.Cog):
    """
    Giphy API - Generate GIFs via a query in a Discord command
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        runs when Cog is loaded and ready to use
        """
        print(f"{self} ready")

    @commands.command(aliases=["gq", "gif", "giphy"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def giphyquery(self, ctx, *query):
        """
        Uses giphy api to search for gifs using user input query strings
        Picks 10 gifs and then randomly chooses 1 to send
        """
        params = parse.urlencode({"q": query, "api_key": giphy_key, "limit": "10"})

        try:
            with request.urlopen("".join((URL, "?", params))) as response:
                data = json.loads(response.read())

                # Check if no GIFs were found
                if not data.get("data"):
                    raise Exception(
                        f"No GIFs found for {' '.join(query)}, try again with a different search query"
                    )

                # Choose a random GIF from the list returned
                selection = random.choice(data["data"])
                link = selection.get("embed_url")
                if link:
                    await ctx.send(link)
                else:
                    raise Exception("No embed URL found for the selected GIF")

        except Exception as e:
            logger.error(
                f"\n\t USER: {ctx.message.author}\n\t INPUT: {query}\n\t ERROR: {e}"
            )
            await ctx.send(f"```{e}```")


async def setup(bot):
    """ """
    await bot.add_cog(Gif_Generator(bot))
