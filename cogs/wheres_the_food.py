"""
Google Maps API integrator Cog for ObamaBot https://github.com/vpaone59
"""

import os

import requests
from discord.ext import commands

from utils.logging_config import create_new_logger

logger = create_new_logger(__name__)

GOOGLE_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"


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
    async def food_search(self, ctx: commands.Context, *keywords: str) -> None:
        """
        Food search command that hits the Google places API and returns
        the nearest restaurant result to the user who called the command.
        """
        kw = " ".join(keywords)

        if not kw:
            await ctx.send("Please tell me what food to search for.")
            return

        try:
            result = find_restaurant(kw, ctx)
        except requests.RequestException as e:
            # The exception text contains the request URL and API key, only log the type
            logger.error("Google Places request failed: %s", type(e).__name__)
            await ctx.send("Couldn't reach Google right now, try again later.")
            return

        await ctx.send(f"```{result}```")


async def setup(bot):
    """
    Adds the cog to the bot
    """
    await bot.add_cog(WheresTheFood(bot))


def find_restaurant(keyword: str, ctx: commands.Context) -> str:
    """
    Create a Google Maps API request targeting restaurants matching param keyword.
    By default, Google will use the IP the command was run from to look for a result.

    param: keyword - The search query.
    param: ctx - The context in which the message was sent.
    """
    logger.info(
        "Function: %s\n User: %s\n Search Keyword: %s",
        __name__,
        ctx.message.author.name,
        keyword,
    )
    data = requests.get(
        TEXT_SEARCH_URL,
        params={"query": keyword, "type": "restaurant", "key": GOOGLE_KEY},
        timeout=15,
    ).json()

    results = data.get("results")
    if not results:
        return f"No results found for {keyword}."

    restaurant = results[0]

    # Google leaves out opening_hours for places without listed hours
    open_now = restaurant.get("opening_hours", {}).get("open_now")
    if open_now is None:
        restaurant_status = "has no listed hours"
    else:
        restaurant_status = "is currently open" if open_now else "is currently closed"

    # Google leaves out the ratings for places that don't have any yet
    if "rating" in restaurant:
        rating_info = f"This location has an Average Rating (out of 5⭐️) of {restaurant['rating']}⭐️, with {restaurant.get('user_ratings_total', 0)} total customer ratings."
    else:
        rating_info = "This location doesn't have any ratings yet."

    message_response = f"We found a result near you for {restaurant['name']}. It's located at {restaurant['formatted_address']} and {restaurant_status}.\n {rating_info}"

    return message_response


def moredetails(placeid: str) -> dict:
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
    data = requests.get(search_url, timeout=15).json()

    return data
