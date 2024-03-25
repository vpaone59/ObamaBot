"""
https://github.com/vpaone59
"""

import os
import datetime
import requests
from discord.ext import commands
from polygon import RESTClient

polygon_key = os.getenv("POLYGON_API_KEY")
client = RESTClient(polygon_key)
url = "https://api.polygon.io/"


class Insider_trading(commands.Cog):
    """
    Polygon.io free tier is limited to 5 api requests per minute
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self} ready")

    @commands.command(aliases=["tick"])
    async def get_ticker_aggregate(self, ctx, ticker):
        """
        Using API and requests to get previous day ticker aggregate
        """
        ticker_param = str(ticker).upper()
        date = datetime.date.today() - datetime.timedelta(1)
        request_url = f"{url}v1/open-close/{ticker_param}/{date}?adjusted=true&sort=asc&limit=120&apiKey={polygon_key}"

        try:
            # Make the API request and get the response
            response = requests.get(request_url)
            response_data = response.json()

            if response.status_code == 404:
                raise Exception(f"Ticker {ticker_param} not found")

            ticker_afterHours = response_data["afterHours"]
            ticker_close = response_data["close"]
            ticker_requested_date = response_data["from"]
            ticker_high = response_data["high"]
            ticker_low = response_data["low"]
            ticker_open = response_data["open"]
            ticker_preMarket = response_data["preMarket"]
            ticker_volume = response_data["volume"]

            # Print out the response data
            await ctx.send(
                f"Previous day for {ticker_param}:\nAfter Hours: {ticker_afterHours}\nClose: {ticker_close}\nRequested Date: {ticker_requested_date}\nHigh: {ticker_high}\nLow: {ticker_low}\nOpen: {ticker_open}\nPre Market: {ticker_preMarket}\nVolume: {ticker_volume}"
            )

        except Exception as e:
            await ctx.send(f"Error occurred while fetching data: {e}")

    @commands.command(aliases=["gpdta"])
    async def get_previous_day_ticker_aggregate(self, ctx, ticker):
        """
        Using the Polygon.io Python library to get previous day ticker aggregate
        """
        previous_day = datetime.date.today() - datetime.timedelta(1)
        ticker_param = str(ticker).upper()
        aggregates = []
        aggregates = client.get_aggs(
            ticker_param,
            1,
            "day",
            previous_day,
            previous_day,
        )
        aggs = aggregates[0]
        agg_open = aggs.open
        agg_high = aggs.high
        agg_low = aggs.low
        agg_close = aggs.close
        agg_volume = aggs.volume
        agg_vwap = aggs.vwap
        agg_timestamp = aggs.timestamp
        agg_transactions = aggs.transactions

        await ctx.send(
            f"Previous day data for {ticker_param}:\nOpen: {agg_open}\nHigh: {agg_high}\nLow: {agg_low}\nClose: {agg_close}\nVolume: {agg_volume}\nVWAP: {agg_vwap}\nTimestamp: {agg_timestamp}\nTransactions: {agg_transactions}"
        )


async def setup(bot):
    await bot.add_cog(Insider_trading(bot))
