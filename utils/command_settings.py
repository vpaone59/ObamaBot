"""
https://github.com/vpaone59

Per server on/off status for commands and features, stored in the guild_commands table.
Statuses are cached in memory so checks don't hit the database on every message.
Anything without a saved status in a server uses its default.
"""

from discord import app_commands
from discord.ext import commands

from .db_helper import get_database_connection, return_database_connection
from .logging_config import create_new_logger

logger = create_new_logger(__name__)

# Features that aren't commands and whether they're on in a server with no saved status.
# Commands are always on by default.
FEATURE_DEFAULTS: dict[str, bool] = {
    "british": False,
}

# Cached statuses, (guild_id, name) -> enabled
_statuses: dict[tuple[int, str], bool] = {}


def load_command_statuses() -> None:
    """
    Load every saved status from the database into the cache. Called once at startup.
    """
    conn = get_database_connection()
    try:
        with conn, conn.cursor() as cursor:
            cursor.execute("SELECT guild_id, command_name, enabled FROM guild_commands")
            rows = cursor.fetchall()
    finally:
        return_database_connection(conn)

    _statuses.clear()
    _statuses.update({(guild_id, name): enabled for guild_id, name, enabled in rows})
    logger.info("Loaded %d saved command statuses", len(_statuses))


def is_enabled(guild_id: int, name: str) -> bool:
    """
    Check if a command or feature is on in a server.

    param: guild_id - The server to check
    param: name - The command's qualified name or the feature name
    """
    return _statuses.get((guild_id, name), FEATURE_DEFAULTS.get(name, True))


def is_command_enabled(
    guild_id: int, command: commands.Command | app_commands.Command
) -> bool:
    """
    Check if a prefix or slash command is on in a server.
    A command is off when it or any group it belongs to is turned off.
    """
    current = command
    while current is not None:
        if not is_enabled(guild_id, current.qualified_name):
            return False
        current = current.parent
    return True


def get_guild_statuses(guild_id: int) -> dict[str, bool]:
    """
    Return the saved statuses for a server, name -> enabled.
    """
    return {
        name: enabled
        for (status_guild_id, name), enabled in _statuses.items()
        if status_guild_id == guild_id
    }


def set_status(guild_id: int, name: str, enabled: bool, updated_by: int) -> None:
    """
    Turn a command or feature on or off in a server.

    param: guild_id - The server to update
    param: name - The command's qualified name or the feature name
    param: enabled - True to turn it on, False to turn it off
    param: updated_by - Discord ID of the user who made the change
    """
    conn = get_database_connection()
    try:
        with conn, conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO guild_commands (guild_id, command_name, enabled, updated_by)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (guild_id, command_name)
                DO UPDATE SET enabled = EXCLUDED.enabled,
                              updated_by = EXCLUDED.updated_by,
                              updated_at = CURRENT_TIMESTAMP
                """,
                (guild_id, name, enabled, updated_by),
            )
    finally:
        return_database_connection(conn)

    _statuses[(guild_id, name)] = enabled
    logger.info(
        "Command status set | Guild: %s | Name: %s | Enabled: %s | By: %s",
        guild_id,
        name,
        enabled,
        updated_by,
    )


def reset_status(guild_id: int, name: str) -> None:
    """
    Remove the saved status for a command or feature so the server uses its default.
    """
    conn = get_database_connection()
    try:
        with conn, conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM guild_commands WHERE guild_id = %s AND command_name = %s",
                (guild_id, name),
            )
    finally:
        return_database_connection(conn)

    _statuses.pop((guild_id, name), None)
    logger.info("Command status reset | Guild: %s | Name: %s", guild_id, name)
