"""
Giphy API integrator Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

Utilizes the Giphy API
"""

import json
import os
import random
from urllib import parse, request

import discord
from discord import app_commands
from discord.ext import commands
from logging_config import create_new_logger

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
        Search for GIFs using the Giphy API and return a random GIF from the results.

        Args:
            query: The search term for finding GIFs
        """
        logger.info("User %s requested GIF for query: %s", interaction.user, query)

        # Validate inputs
        if not GIPHY_KEY:
            logger.error("GIPHY_KEY not configured")
            await interaction.response.send_message(
                "Giphy API is not configured. Please contact an administrator."
            )
            return

        if not query.strip():
            await interaction.response.send_message(
                "Please provide a search term for the GIF."
            )
            return

        # Sanitize query
        query = query.strip()[:100]  # Limit query length

        try:
            params = parse.urlencode(
                {
                    "q": query,
                    "api_key": GIPHY_KEY,
                    "limit": "10",
                    "rating": "pg-13",  # Keep content appropriate
                }
            )

            logger.info("Making Giphy API request for query: %s", query)

            with request.urlopen("".join((URL, "?", params)), timeout=10) as response:
                if response.status != 200:
                    logger.error("Giphy API returned status code: %s", response.status)
                    raise Exception(f"Giphy API error (status {response.status})")

                data = json.loads(response.read())

                # Validate API response
                if "data" not in data:
                    logger.error("Invalid API response structure: %s", data)
                    raise Exception("Invalid response from Giphy API")

                # Check if no GIFs were found
                if not data["data"]:
                    logger.info("No GIFs found for query: %s", query)
                    await interaction.response.send_message(
                        f"No GIFs found for **{query}**\nTry a different search term!"
                    )
                    return

                # Choose a random GIF from the results
                selection = random.choice(data["data"])

                # Get the best available URL (prefer embed_url, fallback to url)
                gif_url = selection.get("embed_url") or selection.get("url")

                if not gif_url:
                    logger.error("No valid URL found in GIF data: %s", selection)
                    raise Exception("No valid URL found for the selected GIF")

                title = selection.get("title", "GIF")[:100]  # Limit title length

                logger.info("Successfully found GIF for query '%s': %s", query, title)

                embed = discord.Embed(
                    title=f"{query}",
                    description=f"[{title}]({gif_url})",
                    color=0xFF6F91,  # Giphy pink
                )
                embed.set_image(url=gif_url)

                await interaction.response.send_message(embed=embed)

        except Exception as e:
            logger.error(
                "Error in GIF search - User: %s, Query: %s, Error: %s",
                interaction.user,
                query,
                e,
                exc_info=True,
            )

            # Provide user-friendly error messages
            if "timeout" in str(e).lower():
                error_msg = "The request timed out. Please try again."
            elif "no gifs found" in str(e).lower():
                error_msg = (
                    f"No GIFs found for **{query}**. Try a different search term!"
                )
            else:
                error_msg = (
                    "Sorry, I couldn't fetch a GIF right now. Please try again later."
                )

            await interaction.response.send_message(error_msg)


async def setup(bot):
    """ """
    await bot.add_cog(GifGenerator(bot))
