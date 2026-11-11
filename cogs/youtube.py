"""
YouTube API integrator Cog for ObamaBot https://github.com/vpaone59
"""

import asyncio
import os
from datetime import datetime

import googleapiclient.discovery
import httplib2
from discord.ext import commands
from googleapiclient.errors import HttpError

from utils.logging_config import create_new_logger

logger = create_new_logger(__name__)
# Rate My Takeaway's YouTube channel ID
RATEMYTAKEAWAY_YOUTUBE_CHANNEL_ID = "UCd03Ksc7VNypelv_TM3SjSg"


class Youtube(commands.Cog):
    """
    YouTube API integrations Class
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Runs when the cog is loaded
        """
        logger.info("%s ready", self.__cog_name__)

    @commands.command(aliases=["get latest video", "latest video", "latest"])
    async def get_latest_video_command(
        self,
        ctx: commands.Context,
        youtube_channel_id: str = RATEMYTAKEAWAY_YOUTUBE_CHANNEL_ID,
    ) -> None:
        """
        Get the most recent upload from any YouTube channel by their channel ID
        Default channel ID is set to Rate My Takeaway's channel ID
        """
        latest_video = await asyncio.to_thread(
            query_latest_youtube_video_from_channel_id, youtube_channel_id
        )

        if latest_video is None:
            await ctx.send("Couldn't find a latest video for that channel.")
            return

        await ctx.send(f"{latest_video['title']} - {latest_video['video_url']}")


def query_latest_youtube_video_from_channel_id(
    youtube_channel_id: str = RATEMYTAKEAWAY_YOUTUBE_CHANNEL_ID,
) -> dict | None:
    """
    Get the most recent upload from any YouTube channel by their channel ID
    Default channel ID is set to Rate My Takeaway's channel ID

    Returns the video details or None if there's no video or the request failed
    """
    youtube_client = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY")
    )

    # Setup for the first request to get the most recent video from the channel
    youtube_video_request = youtube_client.search().list(
        part="snippet",
        channelId=youtube_channel_id,
        type="video",  # Only videos have a videoId, skip playlists
        order="date",  # Order by date so we know it is the most recent
        maxResults=1,  # Fetch one result aka most recent video
    )

    try:
        video_response = youtube_video_request.execute()
    except (HttpError, httplib2.HttpLib2Error, OSError) as e:
        # HttpError text contains the request URL and API key, only log the type
        logger.error("Error fetching latest video: %s", type(e).__name__)
        return None

    if not video_response.get("items"):
        logger.info("No videos found for channel %s", youtube_channel_id)
        return None

    result = video_response["items"][0]
    video_snippet = result["snippet"]

    # Convert the publishedAt string to a datetime object
    published_at_str = video_snippet["publishedAt"]
    published_at = datetime.strptime(published_at_str, "%Y-%m-%dT%H:%M:%SZ")
    # Format it in a readable way
    formatted_published_at = published_at.strftime("%B %d, %Y %H:%M:%S")

    return {
        "title": video_snippet["title"],
        "description": video_snippet["description"],
        "published_at": formatted_published_at,
        "thumbnail": video_snippet["thumbnails"]["medium"]["url"],
        "video_url": f"https://www.youtube.com/watch?v={result['id']['videoId']}",
    }


async def setup(bot):
    """
    Add the cog to the bot
    """
    await bot.add_cog(Youtube(bot))
