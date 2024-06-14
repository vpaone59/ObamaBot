"""
YouTube API integrator Cog for ObamaBot https://github.com/vpaone59
"""

import os
from datetime import datetime
import logging
from discord.ext import commands
import googleapiclient.discovery

# Rate My Takeaway's YouTube channel ID
RATEMYTAKEAWAY_YOUTUBE_CHANNEL_ID = "UCd03Ksc7VNypelv_TM3SjSg"
logger = logging.getLogger(__name__)


class Youtube(commands.Cog):
    """
    YouTube API integrations Class
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["get latest video", "latest video", "latest"])
    async def get_latest_video_command(
        self, ctx, youtube_channel_id=RATEMYTAKEAWAY_YOUTUBE_CHANNEL_ID
    ):
        """
        Get the most recent upload from any YouTube channel by their channel ID
        Default channel ID is set to Rate My Takeaway's channel ID
        """
        await query_latest_youtube_video_from_channel_id(youtube_channel_id)


def query_latest_youtube_video_from_channel_id(
    self, youtube_channel_id=RATEMYTAKEAWAY_YOUTUBE_CHANNEL_ID
):
    """
    Get the most recent upload from any YouTube channel by their channel ID
    Default channel ID is set to Rate My Takeaway's channel ID
    """
    youtube_client = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY")
    )

    # Setup for the first request to get the most recent video from the channel
    youtube_video_request = getattr(youtube_client, "search")().list(
        part="snippet",
        channelId=youtube_channel_id,
        order="date",  # Order by date so we know it is the most recent
        maxResults=1,  # Fetch one result aka most recent video
    )

    try:
        video_response = youtube_video_request.execute()
        if "items" in video_response:
            result = video_response["items"][0]
            video_snippet = result["snippet"]

            # Convert the publishedAt string to a datetime object
            published_at_str = video_snippet["publishedAt"]
            published_at = datetime.strptime(published_at_str, "%Y-%m-%dT%H:%M:%SZ")
            # Format it in a readable way
            formatted_published_at = published_at.strftime("%B %d, %Y %H:%M:%S")

            latest_video = {
                "title": video_snippet["title"],
                "description": video_snippet["description"],
                "published_at": formatted_published_at,
                "thumbnail": video_snippet["thumbnails"]["medium"]["url"],
                "video_url": f"https://www.youtube.com/watch?v={result['id']['videoId']}",
            }

        return latest_video

    except Exception as e:
        # Log any errors that occur during the process
        print(f"Error fetching latest video: {e}")


async def setup(bot):
    """
    Add the cog to the bot
    """
    await bot.add_cog(Youtube(bot))
