"""Minecraft server monitoring cog for tracking player activity and server events."""

import asyncio
import gzip
import os
import re
from datetime import UTC, datetime

import aiofiles
import asyncpg
import discord
from discord import app_commands
from discord.ext import commands, tasks

from utils.logging_config import create_new_logger

logger = create_new_logger(__name__)

# Environment variables
MINECRAFT_LOG_PATH = os.getenv(
    "MINECRAFT_LOG_PATH", "/mnt/cache/appdata/minecraft/logs/latest.log"
)
ACTIVITY_CHANNEL_ID = int(os.getenv("DISCORD_ACTIVITY_CHANNEL_ID", "0") or "0")
SECURITY_CHANNEL_ID = int(os.getenv("DISCORD_SECURITY_CHANNEL_ID", "0") or "0")
MAX_PLAYERS = 20

# Regex patterns for Minecraft server log parsing
PLAYER_JOIN_PATTERN = re.compile(r"\[.*?\].*?(\w+) joined the game|(\w+).*?logged in")
PLAYER_LEAVE_PATTERN = re.compile(r"\[.*?\].*?(\w+) left the game|(\w+).*?disconnected")
PLAYER_IP_PATTERN = re.compile(r"(\w+)\[.*?/(\d+\.\d+\.\d+\.\d+).*?\]")
UNAUTHORIZED_PATTERN = re.compile(
    r"(\w+).*?(Unauthorized|not whitelisted|banned|kicked)", re.IGNORECASE
)


class MinecraftMonitor(commands.Cog):
    """Cog for monitoring Minecraft server logs and player activity."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the MinecraftMonitor cog.

        Args:
            bot: The Discord bot instance.
        """
        self.bot = bot
        self.pool: asyncpg.Pool | None = None
        self.online_players: set[str] = set()
        self.log_file_position: int = 0

    async def cog_load(self) -> None:
        """Initialize the asyncpg connection pool when cog loads."""
        try:
            host = os.getenv("DATABASE_HOST", "localhost")
            port = int(os.getenv("DATABASE_PORT", "5432"))
            database = os.getenv("DATABASE_NAME", "obamabot")
            user = os.getenv("DATABASE_USER", "obamabot")
            password = os.getenv("DATABASE_PASSWORD", "")

            self.pool = await asyncpg.create_pool(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                min_size=1,
                max_size=5,
            )
            logger.info("Minecraft Monitor: asyncpg pool initialized")
        except asyncpg.Error as e:
            logger.error("Minecraft Monitor: Failed to initialize asyncpg pool: %s", e)
            raise

    async def cog_unload(self) -> None:
        """Close the asyncpg connection pool when cog unloads."""
        if self.pool:
            await self.pool.close()
            logger.info("Minecraft Monitor: asyncpg pool closed")

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Start the log tailing task when bot is ready."""
        if not self.tail_minecraft_log.is_running():
            self.tail_minecraft_log.start()
            logger.info("%s ready - log tailing started", self.__cog_name__)

    @tasks.loop(seconds=2)
    async def tail_minecraft_log(self) -> None:
        """Continuously tail the Minecraft latest.log file and process events."""
        if not os.path.exists(MINECRAFT_LOG_PATH):
            logger.warning("Minecraft log file not found: %s", MINECRAFT_LOG_PATH)
            return

        try:
            async with aiofiles.open(MINECRAFT_LOG_PATH, "r", encoding="utf-8") as file:
                # Seek to saved position or end of file on first run
                if self.log_file_position == 0:
                    await file.seek(0, 2)  # Seek to end
                    self.log_file_position = await file.tell()
                else:
                    await file.seek(self.log_file_position)

                # Read new lines
                async for line in file:
                    self.log_file_position = await file.tell()
                    await self._process_log_line(line.strip())

        except OSError as e:
            logger.error("Minecraft Monitor: Error reading log file: %s", e)
        except asyncio.CancelledError:
            logger.info("Minecraft Monitor: Log tailing task cancelled")

    async def _process_log_line(self, line: str) -> None:
        """Process a single line from the Minecraft log.

        Args:
            line: A line from the Minecraft server log.
        """
        if not line:
            return

        # Check for player join
        if "joined the game" in line or "logged in" in line:
            await self._handle_player_join(line)
        # Check for player leave
        elif "left the game" in line or "disconnected" in line:
            await self._handle_player_leave(line)
        # Check for unauthorized connections
        elif "Unauthorized" in line or "not whitelisted" in line:
            await self._handle_unauthorized_attempt(line)

    async def _handle_player_join(self, line: str) -> None:
        """Handle a player join event.

        Args:
            line: The log line containing the join event.
        """
        # Extract player username
        match = PLAYER_JOIN_PATTERN.search(line)
        if not match:
            return

        player = match.group(1) or match.group(2)
        if not player:
            return

        self.online_players.add(player)
        logger.info("Minecraft Monitor: %s joined", player)

        try:
            # Query/update player stats in database
            if not self.pool:
                logger.error("Minecraft Monitor: Database pool not initialized")
                return

            async with self.pool.acquire() as conn:
                # Get or create player record
                player_data = await conn.fetchrow(
                    """
                    SELECT first_login, last_login, login_streak FROM minecraft_players
                    WHERE username = $1
                    """,
                    player,
                )

                if player_data:
                    # Player exists - update login info
                    last_logout = await conn.fetchval(
                        "SELECT last_logout FROM minecraft_players WHERE username = $1",
                        player,
                    )

                    # Calculate streak (if logged out today or yesterday, continue streak)
                    streak = player_data["login_streak"]
                    if last_logout:
                        days_since_logout = (datetime.now(UTC) - last_logout).days
                        if days_since_logout <= 1:
                            streak += 1
                        else:
                            streak = 1
                    else:
                        streak = 1

                    await conn.execute(
                        """
                        UPDATE minecraft_players
                        SET last_login = CURRENT_TIMESTAMP,
                            login_count = login_count + 1,
                            login_streak = $2,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE username = $1
                        """,
                        player,
                        streak,
                    )

                    first_login_str = player_data["first_login"].strftime("%Y-%m-%d")
                else:
                    # New player - create record
                    await conn.execute(
                        """
                        INSERT INTO minecraft_players
                        (username, first_login, last_login, login_count, login_streak)
                        VALUES ($1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1, 1)
                        """,
                        player,
                    )
                    first_login_str = datetime.now(UTC).strftime("%Y-%m-%d")
                    streak = 1

                # Send activity embed
                activity_channel = self.bot.get_channel(ACTIVITY_CHANNEL_ID)
                if activity_channel:
                    embed = discord.Embed(
                        title="🟢 Player Joined",
                        description=f"**{player}** joined the server. ({len(self.online_players)}/{MAX_PLAYERS})",
                        color=discord.Color.green(),
                        timestamp=datetime.now(UTC),
                    )
                    embed.add_field(name="Streak", value=f"{streak} days", inline=True)
                    embed.add_field(
                        name="First Seen", value=first_login_str, inline=True
                    )
                    try:
                        await activity_channel.send(embed=embed)
                    except discord.DiscordException as e:
                        logger.error(
                            "Minecraft Monitor: Failed to send join embed: %s", e
                        )

        except asyncpg.Error as e:
            logger.error("Minecraft Monitor: Database error on player join: %s", e)

    async def _handle_player_leave(self, line: str) -> None:
        """Handle a player leave event.

        Args:
            line: The log line containing the leave event.
        """
        # Extract player username
        match = PLAYER_LEAVE_PATTERN.search(line)
        if not match:
            return

        player = match.group(1) or match.group(2)
        if not player:
            return

        self.online_players.discard(player)
        logger.info("Minecraft Monitor: %s left", player)

        try:
            # Update player's last logout time
            if self.pool:
                async with self.pool.acquire() as conn:
                    await conn.execute(
                        """
                        UPDATE minecraft_players
                        SET last_logout = CURRENT_TIMESTAMP,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE username = $1
                        """,
                        player,
                    )

            # Send activity embed
            activity_channel = self.bot.get_channel(ACTIVITY_CHANNEL_ID)
            if activity_channel:
                embed = discord.Embed(
                    title="🔴 Player Left",
                    description=f"**{player}** left the server. ({len(self.online_players)}/{MAX_PLAYERS})",
                    color=discord.Color.red(),
                    timestamp=datetime.now(UTC),
                )
                try:
                    await activity_channel.send(embed=embed)
                except discord.DiscordException as e:
                    logger.error("Minecraft Monitor: Failed to send leave embed: %s", e)

        except asyncpg.Error as e:
            logger.error("Minecraft Monitor: Database error on player leave: %s", e)

    async def _handle_unauthorized_attempt(self, line: str) -> None:
        """Handle an unauthorized connection attempt.

        Args:
            line: The log line containing the unauthorized event.
        """
        # Extract player and reason
        match = UNAUTHORIZED_PATTERN.search(line)
        if not match:
            return

        player = match.group(1) if match else "Unknown"
        reason = match.group(2) if match else "Unknown reason"

        logger.warning(
            "Minecraft Monitor: Unauthorized attempt from %s: %s", player, reason
        )

        # Send security alert
        security_channel = self.bot.get_channel(SECURITY_CHANNEL_ID)
        if security_channel:
            embed = discord.Embed(
                title="⚠️ Unauthorized Connection Attempt",
                color=discord.Color.orange(),
                timestamp=datetime.now(UTC),
            )
            embed.add_field(name="User", value=player, inline=True)
            embed.add_field(name="Reason", value=reason, inline=True)

            # Extract IP if available
            ip_match = PLAYER_IP_PATTERN.search(line)
            if ip_match:
                ip = ip_match.group(2)
                embed.add_field(name="IP", value=ip, inline=True)

            try:
                await security_channel.send(embed=embed)
            except discord.DiscordException as e:
                logger.error("Minecraft Monitor: Failed to send security alert: %s", e)

    @app_commands.command(name="mcstatus")
    async def mc_status(self, interaction: discord.Interaction) -> None:
        """Display the current Minecraft server status and top players.

        Args:
            interaction: The Discord interaction (slash command invocation).
        """
        if not self.pool:
            await interaction.response.send_message(
                "❌ Database connection not available.", ephemeral=True
            )
            return

        try:
            async with self.pool.acquire() as conn:
                # Get top 5 longest login streaks
                top_streaks = await conn.fetch(
                    """
                    SELECT username, login_streak, last_login
                    FROM minecraft_players
                    ORDER BY login_streak DESC
                    LIMIT 5
                    """
                )

                # Create embed
                embed = discord.Embed(
                    title="🎮 Minecraft Server Status",
                    description=f"**Current Players:** {len(self.online_players)}/{MAX_PLAYERS}",
                    color=discord.Color.blue(),
                    timestamp=datetime.now(UTC),
                )

                # Add online players field
                if self.online_players:
                    players_str = ", ".join(sorted(self.online_players))
                    embed.add_field(
                        name="Online Players",
                        value=players_str,
                        inline=False,
                    )
                else:
                    embed.add_field(
                        name="Online Players",
                        value="*No players online*",
                        inline=False,
                    )

                # Add top streaks field
                if top_streaks:
                    streaks_str = "\n".join(
                        [
                            f"**{i + 1}.** {row['username']}: {row['login_streak']} days"
                            for i, row in enumerate(top_streaks)
                        ]
                    )
                    embed.add_field(
                        name="Top 5 Login Streaks",
                        value=streaks_str,
                        inline=False,
                    )
                else:
                    embed.add_field(
                        name="Top 5 Login Streaks",
                        value="*No player data yet*",
                        inline=False,
                    )

                await interaction.response.send_message(embed=embed)

        except asyncpg.Error as e:
            logger.error("Minecraft Monitor: Database error in /mcstatus: %s", e)
            await interaction.response.send_message(
                f"❌ Database error: {e}", ephemeral=True
            )

    @app_commands.command(name="mcsync")
    @app_commands.checks.has_permissions(administrator=True)
    async def mc_sync(self, interaction: discord.Interaction) -> None:
        """Sync Minecraft logs with database (admin only).

        Reads through all available log files and ensures player data is current.
        This command scans historical logs for join/leave events and updates the
        database if new data is found. Useful when starting the bot or if you
        suspect data is out of sync.

        Args:
            interaction: The Discord interaction (slash command invocation).
        """
        await interaction.response.defer()
        try:
            stats = await self._sync_historical_logs()
            embed = discord.Embed(
                title="✅ Minecraft Log Sync Complete",
                color=discord.Color.green(),
                timestamp=datetime.now(UTC),
            )
            embed.add_field(
                name="Joins Processed", value=str(stats["joins"]), inline=True
            )
            embed.add_field(
                name="Leaves Processed", value=str(stats["leaves"]), inline=True
            )
            embed.add_field(
                name="Unauthorized Events",
                value=str(stats["unauthorized"]),
                inline=True,
            )
            embed.add_field(
                name="Files Scanned", value=str(stats["files"]), inline=True
            )
            await interaction.followup.send(embed=embed)
            logger.info("Minecraft Monitor: Sync complete - %s", stats)
        except Exception as e:
            logger.error("Minecraft Monitor: Error syncing logs: %s", e)
            await interaction.followup.send(f"❌ Sync failed: {e}", ephemeral=True)

    async def _sync_historical_logs(self) -> dict[str, int]:
        """Scan through historical log files and sync player data.

        Reads latest.log, latest.log.1, latest.log.2, etc. and processes
        all join/leave/unauthorized events found.

        Returns:
            dict: Statistics about the sync (joins, leaves, unauthorized, files).
        """

        log_dir = os.path.dirname(MINECRAFT_LOG_PATH)
        log_filename = os.path.basename(MINECRAFT_LOG_PATH)
        stats = {"joins": 0, "leaves": 0, "unauthorized": 0, "files": 0}

        if not os.path.exists(log_dir):
            logger.warning("Minecraft Monitor: Log directory not found: %s", log_dir)
            return stats

        # Find all log files (latest.log, latest.log.1, latest.log.2.gz, etc.)
        log_files = []
        try:
            for filename in sorted(os.listdir(log_dir), reverse=True):
                if filename.startswith(log_filename):
                    full_path = os.path.join(log_dir, filename)
                    log_files.append(full_path)
        except OSError as e:
            logger.error("Minecraft Monitor: Error listing log files: %s", e)
            return stats

        logger.info("Minecraft Monitor: Found %d log files to sync", len(log_files))

        # Process each log file in reverse chronological order (newest first)
        for log_file in log_files:
            stats["files"] += 1
            logger.info("Minecraft Monitor: Syncing %s", log_file)

            try:
                # Handle gzipped files
                if log_file.endswith(".gz"):
                    async with aiofiles.open(log_file, "rb") as f:
                        content = await f.read()
                        lines = gzip.decompress(content).decode("utf-8").splitlines()
                else:
                    async with aiofiles.open(log_file, "r", encoding="utf-8") as f:
                        lines = await f.readlines()

                # Process each line
                for line in lines:
                    line = line.strip() if isinstance(line, str) else line
                    if not line:
                        continue

                    # Count events (don't send embeds during sync, just update DB)
                    if "joined the game" in line or "logged in" in line:
                        await self._sync_player_join(line)
                        stats["joins"] += 1
                    elif "left the game" in line or "disconnected" in line:
                        await self._sync_player_leave(line)
                        stats["leaves"] += 1
                    elif "Unauthorized" in line or "not whitelisted" in line:
                        stats["unauthorized"] += 1

            except (OSError, IOError, gzip.BadGzipFile) as e:
                logger.error(
                    "Minecraft Monitor: Error reading log file %s: %s", log_file, e
                )
                continue

        return stats

    async def _sync_player_join(self, line: str) -> None:
        """Sync a player join event (database only, no embed).

        Args:
            line: The log line containing the join event.
        """
        match = PLAYER_JOIN_PATTERN.search(line)
        if not match:
            return

        player = match.group(1) or match.group(2)
        if not player or not self.pool:
            return

        try:
            async with self.pool.acquire() as conn:
                player_data = await conn.fetchrow(
                    """
                    SELECT first_login, last_login, login_streak FROM minecraft_players
                    WHERE username = $1
                    """,
                    player,
                )

                if player_data:
                    # Player exists - update login info
                    last_logout = await conn.fetchval(
                        "SELECT last_logout FROM minecraft_players WHERE username = $1",
                        player,
                    )

                    # Calculate streak
                    streak = player_data["login_streak"]
                    if last_logout:
                        days_since_logout = (datetime.now(UTC) - last_logout).days
                        if days_since_logout <= 1:
                            streak += 1
                        else:
                            streak = 1
                    else:
                        streak = 1

                    await conn.execute(
                        """
                        UPDATE minecraft_players
                        SET last_login = CURRENT_TIMESTAMP,
                            login_count = login_count + 1,
                            login_streak = $2,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE username = $1
                        """,
                        player,
                        streak,
                    )
                else:
                    # New player - create record
                    await conn.execute(
                        """
                        INSERT INTO minecraft_players
                        (username, first_login, last_login, login_count, login_streak)
                        VALUES ($1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1, 1)
                        """,
                        player,
                    )

        except asyncpg.Error as e:
            logger.error("Minecraft Monitor: Database error in sync join: %s", e)

    async def _sync_player_leave(self, line: str) -> None:
        """Sync a player leave event (database only, no embed).

        Args:
            line: The log line containing the leave event.
        """
        match = PLAYER_LEAVE_PATTERN.search(line)
        if not match:
            return

        player = match.group(1) or match.group(2)
        if not player or not self.pool:
            return

        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    UPDATE minecraft_players
                    SET last_logout = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE username = $1
                    """,
                    player,
                )
        except asyncpg.Error as e:
            logger.error("Minecraft Monitor: Database error in sync leave: %s", e)


async def setup(bot: commands.Bot) -> None:
    """Load the MinecraftMonitor cog.

    Args:
        bot: The Discord bot instance.
    """
    # Check if required environment variables are set
    if not ACTIVITY_CHANNEL_ID or not SECURITY_CHANNEL_ID:
        logger.error(
            "MinecraftMonitor: DISCORD_ACTIVITY_CHANNEL_ID or DISCORD_SECURITY_CHANNEL_ID not set. Cog not loaded."
        )
        return

    if not os.path.exists(MINECRAFT_LOG_PATH):
        logger.warning(
            "MinecraftMonitor: MINECRAFT_LOG_PATH does not exist: %s",
            MINECRAFT_LOG_PATH,
        )

    await bot.add_cog(MinecraftMonitor(bot))
    logger.info("MinecraftMonitor cog loaded")
