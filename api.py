"""
FastAPI server for Discord bot stats integration.
Exposes server stats endpoints and handles backend communication.
"""

import os

import httpx
from fastapi import FastAPI, HTTPException
from uvicorn import Config, Server

from utils.logging_config import create_new_logger

logger = create_new_logger(__name__)

# FastAPI app instance
app = FastAPI(title="ObamaBot API", version="1.0.0")

# Global bot reference (will be set by main.py)
bot = None

# Backend configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
BACKEND_TIMEOUT = 10


def set_bot_reference(bot_instance):
    """
    Called from main.py to set the bot reference.
    This allows the API to access bot data.
    """
    global bot
    bot = bot_instance
    logger.info("Bot reference set for API server")


async def ping_backend():
    """
    Pings the backend to ensure connectivity.
    Returns True if successful, False otherwise.
    """
    try:
        async with httpx.AsyncClient(timeout=BACKEND_TIMEOUT) as client:
            response = await client.get(f"{BACKEND_URL}/api/servers/sync/")
            if response.status_code == 200:
                logger.info("Backend ping successful - stats synced")
                return True
            else:
                logger.warning(
                    "Backend returned status %s: %s",
                    response.status_code,
                    response.text,
                )
                return False
    except httpx.ConnectError:
        logger.warning("Could not connect to backend at %s", BACKEND_URL)
        return False
    except httpx.TimeoutException:
        logger.warning("Backend connection timed out (%ss)", BACKEND_TIMEOUT)
        return False
    except Exception as e:
        logger.warning("Error pinging backend: %s", e)
        return False


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "bot": bot.user.name if bot else "disconnected"}


@app.get("/api/servers")
async def get_all_servers():
    """
    Returns stats for all servers the bot is a member of.

    Response format:
    [
        {
            "server_id": 1040708391921786901,
            "name": "CutieCatClub",
            "member_count": 150,
            "description": "Server description or None",
            "icon_url": "https://cdn.discordapp.com/..."
        },
        ...
    ]
    """
    if not bot:
        raise HTTPException(status_code=503, detail="Bot not connected")

    servers = []
    for guild in bot.guilds:
        server_data = {
            "server_id": guild.id,
            "name": guild.name,
            "member_count": guild.member_count,
            "description": guild.description,
            "icon_url": str(guild.icon.url) if guild.icon else None,
        }
        servers.append(server_data)

    return servers


@app.get("/api/servers/{server_id}")
async def get_server(server_id: int):
    """
    Returns stats for a specific server.
    """
    if not bot:
        raise HTTPException(status_code=503, detail="Bot not connected")

    guild = bot.get_guild(server_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Server not found")

    return {
        "server_id": guild.id,
        "name": guild.name,
        "member_count": guild.member_count,
        "description": guild.description,
        "icon_url": str(guild.icon.url) if guild.icon else None,
    }


@app.post("/api/sync")
async def sync_with_backend():
    """
    Manually trigger a sync with the backend.
    """
    success = await ping_backend()
    return {"success": success, "message": "Sync completed"}


async def run_api_server(host: str = "0.0.0.0", port: int = 5000):
    """
    Runs the FastAPI server in an asyncio task.
    """
    config = Config(app=app, host=host, port=port, log_level="info")
    server = Server(config)

    logger.info("Starting API server on %s:%s", host, port)
    await server.serve()
