"""
Giphy API integrator Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

Utilizes the Giphy API
"""

import random
import os
import json
from urllib import parse, request
from discord.ext import commands
from logging_config import create_new_logger
import discord
from discord import app_commands

logger = create_new_logger(__name__)
# Grab Giphy key & assign url to variable
GIPHY_KEY = os.getenv("GIPHY_KEY")
URL = "http://api.giphy.com/v1/gifs/search"


class GifGenerator(commands.Cog):
    """
    Giphy API - Generate GIFs via a query in a Discord command
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Runs when the cog is loaded
        """
        logger.info("%s ready", self.__cog_name__)

    @app_commands.command(name="gq", description="Search for GIFs using Giphy API")
    @app_commands.describe(query="The search query for the GIFs")
    async def get_random_gif(self, interaction: discord.Interaction, query: str):
        """
        Search for GIFs using the Giphy API and return a random GIF from the results
        """
        params = parse.urlencode({"q": query, "api_key": GIPHY_KEY, "limit": "10"})

        try:
            with request.urlopen("".join((URL, "?", params))) as response:
                data = json.loads(response.read())

                # Check if no GIFs were found
                if not data.get("data"):
                    raise Exception(
                        f"No GIFs found for {query}, try again with a different search query"
                    )

                # Choose a random GIF from the list returned
                selection = random.choice(data["data"])
                link = selection.get("embed_url")
                if link:
                    await interaction.response.send_message(f"{query}\n{link}")
                else:
                    raise Exception("No embed URL found for the selected GIF")

        except Exception as e:
            logger.error(
                f"\n\t USER: {interaction.user}\n\t INPUT: {query}\n\t ERROR: {e}"
            )
            await interaction.response.send_message(f"```{e}```")


async def setup(bot):
    """ """
    await bot.add_cog(GifGenerator(bot))
