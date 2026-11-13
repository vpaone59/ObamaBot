"""
https://github.com/vpaone59

Permission helpers shared by the Cogs.
"""

import os

# Discord user ID of the bot's super admin, the only user who can run super admin commands
SUPER_ADMIN_DISCORD_ID = os.getenv("SUPER_ADMIN_DISCORD_ID")
SUPER_ADMIN_ID = int(SUPER_ADMIN_DISCORD_ID) if SUPER_ADMIN_DISCORD_ID else None


def is_super_admin(user_id: int) -> bool:
    """
    Check if a Discord user is the super admin. Always False when no super admin is set.
    """
    return SUPER_ADMIN_ID is not None and user_id == SUPER_ADMIN_ID
