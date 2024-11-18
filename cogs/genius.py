"""
Genius API integrator Cog for ObamaBot https://github.com/vpaone59
"""

import os
import random
from discord.ext import commands
import lyricsgenius
from logging_config import create_new_logger

logger = create_new_logger(__name__)
GENIUS_API_KEY = os.getenv("GENIUS_API_KEY")


class Genius(commands.Cog):
    """
    Genius API integrations Class
    """

    def __init__(self, bot):
        self.bot = bot
        self.genius = lyricsgenius.Genius(GENIUS_API_KEY)
        # Remove section headers from lyrics
        self.genius.remove_section_headers = True
        # Skip songs that have "remix", "live", etc.
        self.genius.skip_non_songs = True

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Runs when the cog is loaded
        """
        logger.info("%s ready", self.__cog_name__)

    @commands.command(aliases=["random_bar", "bar"])
    async def get_random_bar(self, ctx, *, artist_name: str):
        """
        Get a random bar from a random song in the input artist's discography
        """
        try:
            # Search for artist
            artist = self.genius.search_artist(
                artist_name, max_songs=1, sort="popularity"
            )

            if not artist:
                await ctx.send(f"No artist found with name: {artist_name}")
                return

            # Get a random song from artist's songs
            song = random.choice(artist.songs)

            if not song.lyrics:
                await ctx.send(f"No lyrics found for song: {song.title}")
                return

            # Split lyrics into lines and filter out empty lines
            lyrics_lines = [line for line in song.lyrics.split("\n") if line.strip()]

            # Get a random line
            random_bar = random.choice(lyrics_lines)
            random_bar2 = random.choice(lyrics_lines)

            await ctx.send(f"{random_bar}, {random_bar2}")

        except Exception as e:
            logger.error("Error getting lyrics: %s", e)
            await ctx.send(f"An error occurred: {e}")


async def setup(bot):
    await bot.add_cog(Genius(bot))
