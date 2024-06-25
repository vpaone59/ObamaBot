"""
Roles Cog for ObamaBot by Vincent Paone https://github.com/vpaone59
"""

import discord
from discord.ext import commands
from discord.utils import get
from logging_config import create_new_logger

logger = create_new_logger(__name__)


class Roles(commands.Cog, name="Roles"):
    """
    role related commands for a Bot
    """

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Runs when the cog is loaded
        """
        logger.info("%s ready", self)

    @commands.command(name="hasrole", aliases=["hr"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def hasRole(self, ctx, user: discord.Member = None, check=None):
        """
        check if the mentioned user has the role
        param: @user The user to check a role for
        param: @check The role you want to check if the user has
        """
        if check == None or user == None:
            await ctx.send(
                'Missing argument.\nTo use; $hasRole __@user_mention__ "__role_name__"'
            )
        elif not get(ctx.guild.roles, name=check):
            await ctx.send(
                f"Role **{check}** does not exist in this guild. Use **$listroles** to get a list of this guild's roles."
            )
        else:
            role = discord.utils.find(
                lambda r: r.name == check, ctx.message.guild.roles
            )
            if role in user.roles:
                await ctx.send(f"User {user.mention} has the **{check}** role")
            else:
                await ctx.send(f"User{user.mention} does not have the **{check}** role")

    @commands.command(aliases=["cr"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def createrole(self, ctx, role):
        """
        create a roll in the current guild
        param - role The name of the role you want to create
        """
        # check if the role exists in the guild
        if get(ctx.guild.roles, name=role):
            await ctx.send("Role already exists!")
        else:
            await ctx.guild.create_role(name=role, color=discord.Color(0x0062FF))
            await ctx.send(f"{role} has been created")

    @commands.command(aliases=["dr"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def deleterole(self, ctx, role):
        """
        create a roll in the current guild
        param - role The name of the role you want to delete
        """
        # check if the role exists in the guild
        if get(ctx.guild.roles, name=role) is None:
            await ctx.send("Role does not exist!")
        else:
            r = get(ctx.guild.roles, name=role)
            await r.delete()
            await ctx.send(f"{role} has been deleted")

    @commands.command(aliases=["lr"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def listroles(self, ctx):
        """
        list all of the roles in the current guild
        """
        rls = ""
        for r in ctx.guild.roles:
            rls = rls + "\n" + r.name
        await ctx.send(f"```Roles in {ctx.guild.name}:{rls}```")


async def setup(client):
    await client.add_cog(Roles(client))
