"""Entrypoint file for Nanite.
"""
# Config imports
from .config import BOT_COMMAND_PREFIX, BOT_DESCRIPTION

# Library imports
import discord
import datetime
from loguru import logger

nanite = discord.ext.commands.Bot(BOT_COMMAND_PREFIX, description=BOT_DESCRIPTION)

# Events and commands


@nanite.event()
async def on_ready() -> None:
    """
    Log an INFO message when the bot has successfully connected to the Discord API.
    """
    logger.info(
        f"Successfully connected to the Discord API. Connected as user: {nanite.user}"
    )


@nanite.command()
async def ping(ctx: discord.ext.commands.Context) -> None:
    """Pongs back to check the bot is running. Returns the bot's response time in milliseconds.

    Args:
        ctx (discord.ext.commands.Context): Represents the context in which a command is being invoked under.
    """
    delta = datetime.datetime.now() - ctx.message.created_at
    logger.info(f"Running ping command. Time difference: {time_difference}")
    await ctx.send(
        f"Pong!\n**Latency**: {delta.total_seconds() * 1000}ms",
        embed=discord.Embed(title=":ping_pong:", colour=discord.Colour.red()),
    )
