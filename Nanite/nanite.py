# Settings imports
from .config import BOT_COMMAND_PREFIX, BOT_DESCRIPTION, BOT_STATUS

# Bot imports
import discord
from discord.ext import commands
from loguru import logger
from datetime import datetime

nanite = commands.Bot(BOT_COMMAND_PREFIX, description=BOT_DESCRIPTION)

# Events and commands


@nanite.event()
async def on_ready():
    """
    Runs when the the bot has successfully connected to the Discord API.
    """
    logger.debug(
        f"Successfully connected to the Discord API. Connected as user: {nanite.user}."
    )


@nanite.command()
async def ping(ctx: commands.Context):
    """
    Pongs back to check the bot is running and the response time in milliseconds.

    :param ctx: Holds the context in which a command is invoked under.
    """
    delta = datetime.now() - ctx.message.created_at
    logger.debug(f"Running ping command.\nTime difference: {time_difference}")
    await ctx.send(
        f"Pong!\n**Latency**: {delta.total_seconds() * 1000}ms",
        embed=discord.Embed(title=":ping_pong:", colour=discord.Colour.red()),
    )
