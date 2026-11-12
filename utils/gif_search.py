"""
https://github.com/vpaone59

GIF search helper shared by the Cogs. Tries Klipy first, then Giphy as fallback.
"""

import asyncio
import json
import os
import random
from urllib import parse, request
from urllib.error import URLError

from .logging_config import create_new_logger

logger = create_new_logger(__name__)

# Gif API keys (Klipy primary, Giphy fallback)
KLIPY_KEY = os.getenv("KLIPY_KEY")
KLIPY_API_URL = "https://api.klipy.io/gifs/search"
GIPHY_KEY = os.getenv("GIPHY_KEY")
GIPHY_SEARCH_URL = "https://api.giphy.com/v1/gifs/search"

# Number of results to pick a random GIF from
SEARCH_LIMIT = "25"


async def search_gif(query: str) -> str | None:
    """
    Search for a GIF matching the query, trying Klipy first, then Giphy as fallback.
    Returns the GIF URL, or None if nothing was found or no API is configured.

    param: query - The search term, e.g. "danny devito"
    """
    if not KLIPY_KEY and not GIPHY_KEY:
        logger.error("No GIF APIs configured (KLIPY_KEY and GIPHY_KEY both missing)")
        return None

    if KLIPY_KEY:
        url = await asyncio.to_thread(_fetch_gif_from_klipy, query)
        if url:
            return url

    if GIPHY_KEY:
        url = await asyncio.to_thread(_fetch_gif_from_giphy, query)
        if url:
            return url

    logger.warning("No GIF found for query: %s", query)
    return None


def _fetch_gif_from_klipy(query: str) -> str | None:
    """
    Search Klipy for a GIF and return the URL, or None on failure.
    Blocking call, run with asyncio.to_thread.
    """
    params = parse.urlencode(
        {"query": query, "api_key": KLIPY_KEY, "limit": SEARCH_LIMIT}
    )
    logger.debug("Klipy: Searching for %s", query)

    try:
        with request.urlopen(f"{KLIPY_API_URL}?{params}", timeout=10) as response:
            if response.status != 200:
                logger.error("Klipy API returned status code: %s", response.status)
                return None
            data = json.loads(response.read())

    except (URLError, TimeoutError, ValueError):
        logger.exception("Error fetching GIF from Klipy")
        return None

    results = data.get("gifs") or data.get("data")
    if not results:
        logger.info("No GIFs found on Klipy for query: %s", query)
        return None

    selection = random.choice(results)
    return selection.get("url") or selection.get("embed_url")


def _fetch_gif_from_giphy(query: str) -> str | None:
    """
    Search Giphy for a GIF and return the URL, or None on failure.
    Blocking call, run with asyncio.to_thread.
    """
    params = parse.urlencode(
        {"q": query, "api_key": GIPHY_KEY, "limit": SEARCH_LIMIT, "rating": "pg-13"}
    )
    logger.debug("Giphy: Searching for %s", query)

    try:
        with request.urlopen(f"{GIPHY_SEARCH_URL}?{params}", timeout=10) as response:
            if response.status != 200:
                logger.error("Giphy API returned status code: %s", response.status)
                return None
            data = json.loads(response.read())

    except (URLError, TimeoutError, ValueError):
        logger.exception("Error fetching GIF from Giphy")
        return None

    results = data.get("data")
    if not results:
        logger.info("No GIFs found on Giphy for query: %s", query)
        return None

    # Prefer the GIF file itself so Discord shows it inline
    selection = random.choice(results)
    return selection.get("images", {}).get("original", {}).get("url") or selection.get(
        "url"
    )
