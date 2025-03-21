"""
Google Maps API integrator Cog for ObamaBot https://github.com/vpaone59
"""

import os
from discord.ext import commands
import requests
from logging_config import create_new_logger

logger = create_new_logger(__name__)

GOOGLE_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


class WheresTheFood(commands.Cog):
    """
    Commands using Google's Places API
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Runs when the cog is loaded
        """
        logger.info("%s ready", self.__cog_name__)

    @commands.command()
    async def food_search(self, ctx, *keywords):
        """
        Food search command that hits the Google places API and returns
        the nearest restaurant result to the user who called the command.
        """
        kw = " ".join(keywords)

        result = find_restaurant(kw, ctx)

        await ctx.send(f"```{result}```")


async def setup(bot):
    """
    Adds the cog to the bot
    """
    await bot.add_cog(WheresTheFood(bot))


def find_restaurant(keyword, ctx):
    """
    Create a Google Maps API request targeting restaurants matching param keyword.
    By default, Google will use the IP the command was run from to look for a result.

    param: keyword - The search query.
    param: ctx - The context in which the message was sent.
    """
    search_url = (
        "https://maps.googleapis.com/maps/api/place/textsearch/json?query="
        + keyword
        + "&type=restaurant&key="
        + GOOGLE_KEY
    )

    logger.info(
        "Function: %s\n User: %s\n Search Keyword: %s\n URL: %s",
        __name__,
        ctx.message.author.name,
        keyword,
        search_url,
    )
    data = requests.get(search_url, timeout=15).json()
    restaurant = data["results"][0]

    # Get restaurant open status in a String
    restaurant_status = ""
    if {restaurant["opening_hours"]["open_now"]} is True:
        restaurant_status = "open"
    else:
        restaurant_status = "closed"

    message_response = f"We found a result near you for {restaurant['name']}. It's located at {restaurant['formatted_address']} and is currently {restaurant_status}.\n This location has an Average Rating (out of 5⭐️) of {restaurant['rating']}⭐️, with {restaurant['user_ratings_total']} total customer ratings."

    return message_response


def moredetails(placeid):
    """
    Using the place_id generated from googlefoods() we can make
    another API call to get information that textsearch can't get

    params: placeid - The place_id generated from googlefoods()
    """
    search_url = (
        "https://maps.googleapis.com/maps/api/place/details/json?place_id="
        + placeid
        + "&key="
        + GOOGLE_KEY
    )
    print(search_url)
    data = requests.get(search_url, timeout=15).json()

    return data
