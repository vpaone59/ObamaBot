"""
Server Commands Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

Turn commands and features on or off for a specific server.
Only the super admin can use these commands for now.
"""

import discord
import psycopg2
from discord.ext import commands

from utils.checks import is_super_admin
from utils.command_settings import (
    FEATURE_DEFAULTS,
    get_guild_statuses,
    is_enabled,
    reset_status,
    set_status,
)
from utils.logging_config import create_new_logger

logger = create_new_logger(__name__)

# Commands that can't be turned off so the bot can always be managed
PROTECTED_COMMANDS = {"command", "cog", "sync"}


class ServerCommands(commands.Cog):
    """
    Per server command and feature settings
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Runs when the cog is loaded
        """
        logger.info("%s ready", self.__cog_name__)

    async def cog_check(self, ctx: commands.Context) -> bool:
        """
        Every command in this Cog is super admin only and must be run in a server
        """
        return ctx.guild is not None and is_super_admin(ctx.author.id)

    @commands.group(name="command", aliases=["cmd"], invoke_without_command=True)
    async def command_group(self, ctx: commands.Context) -> None:
        """
        Show which commands and features are on or off in this server.

        Usage:
        !command enable <name>
        !command disable <name>
        !command reset <name> (go back to the default)
        """
        await self.send_status(ctx)

    @command_group.command(name="status")
    async def status(self, ctx: commands.Context) -> None:
        """
        Show which commands and features are on or off in this server
        """
        await self.send_status(ctx)

    @command_group.command(name="enable", aliases=["on"])
    async def enable(self, ctx: commands.Context, *, name: str) -> None:
        """
        Turn a command or feature on in this server
        """
        await self.update_status(ctx, name, enabled=True)

    @command_group.command(name="disable", aliases=["off"])
    async def disable(self, ctx: commands.Context, *, name: str) -> None:
        """
        Turn a command or feature off in this server
        """
        await self.update_status(ctx, name, enabled=False)

    @command_group.command(name="reset")
    async def reset(self, ctx: commands.Context, *, name: str) -> None:
        """
        Remove this server's setting for a command or feature so it uses the default
        """
        names = self.resolve_names(ctx, name)
        if not names:
            await ctx.send(f"```No command or feature named {name}```")
            return

        try:
            for resolved_name in names:
                reset_status(ctx.guild.id, resolved_name)
        except psycopg2.Error:
            logger.exception("Failed to reset command status for %s", names)
            await ctx.send("```Couldn't save that change, check the logs```")
            return

        await ctx.send(f"```Reset {', '.join(names)} to the default```")

    async def update_status(
        self, ctx: commands.Context, name: str, enabled: bool
    ) -> None:
        """
        Save a command or feature's status for this server
        """
        names = self.resolve_names(ctx, name)
        if not names:
            await ctx.send(f"```No command or feature named {name}```")
            return

        if not enabled and PROTECTED_COMMANDS.intersection(names):
            await ctx.send(f"```{name} can't be turned off```")
            return

        try:
            for resolved_name in names:
                set_status(ctx.guild.id, resolved_name, enabled, ctx.author.id)
        except psycopg2.Error:
            logger.exception("Failed to save command status for %s", names)
            await ctx.send("```Couldn't save that change, check the logs```")
            return

        state = "on" if enabled else "off"
        await ctx.send(f"```Turned {', '.join(names)} {state} in {ctx.guild.name}```")

    def resolve_names(self, ctx: commands.Context, name: str) -> list[str]:
        """
        Find the saved names for a command or feature.
        Returns both the prefix and slash command when they share a name, e.g. askobama.
        """
        name = name.strip().lower()
        if name in FEATURE_DEFAULTS:
            return [name]

        names = []
        command = self.bot.get_command(name)
        if command is not None:
            names.append(command.qualified_name)

        app_command = self.bot.tree.get_command(name) or self.bot.tree.get_command(
            name, guild=discord.Object(id=ctx.guild.id)
        )
        if app_command is not None and app_command.qualified_name not in names:
            names.append(app_command.qualified_name)

        return names

    async def send_status(self, ctx: commands.Context) -> None:
        """
        Send the features and saved command statuses for this server
        """
        lines = ["Features:"]
        for feature in sorted(FEATURE_DEFAULTS):
            state = "on" if is_enabled(ctx.guild.id, feature) else "off"
            lines.append(f"  {feature}: {state}")

        command_statuses = {
            name: enabled
            for name, enabled in get_guild_statuses(ctx.guild.id).items()
            if name not in FEATURE_DEFAULTS
        }
        lines.append("Commands turned on or off in this server:")
        if command_statuses:
            for name, enabled in sorted(command_statuses.items()):
                lines.append(f"  {name}: {'on' if enabled else 'off'}")
        else:
            lines.append("  none, every command is on")

        await ctx.send("```" + "\n".join(lines) + "```")


async def setup(bot):
    await bot.add_cog(ServerCommands(bot))
