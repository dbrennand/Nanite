# Settings imports
from .config import BOT_DEFAULT_PLANETSIDE2_SERVER

# Bot imports
import discord
import aiohttp
import auraxium
from discord.ext import commands
from loguru import logger


class Planetside2(commands.Bot):
    """
    Class for the Planetside 2 Discord bot Cog.

    Groups Planetside 2 related bot commands.
    """

    def __init__(self, bot: commands.Bot):
        """
        Initalisation class for Planetside 2 class.
        """
        self.bot = bot

    # Helpers functions

    async def get_json(self, session: aiohttp.ClientSession, endpoint: str) -> dict:
        """
        Retrieve JSON from a specified API endpoint.

        :param endpoint: The URL for the API endpoint to retrieve JSON from.
        :returns: A dictionary object containing the JSON response (if any).
        :raises HTTPException: Occurs when a HTTP status code other than 200 occurs.
        """
        logger.debug(f"Endpoint: {endpoint}.")
        async with session.get(endpoint, raise_for_status=True) as resp:
            return await resp.json()

    # Events and commands

    @commands.command()
    async def population(
        self, ctx: commands.Context, server: str = BOT_DEFAULT_PLANETSIDE2_SERVER
    ):
        """
        Get current population data for a specific server.

        Defaults to current time.

        [API documentation](https://ps2.fisu.pw/api/population/).

        :param server: The name of the server to retrieve population data for.
        """
        servers = {
            "connery": 1,
            "miller": 10,
            "cobalt": 13,
            "emerald": 17,
            "jaeger": 19,
            "apex": 24,
            "solTech": 40,
        }
        capital_server = server.capitalize()
        choice = servers.get(server.lower(), None)
        if choice:
            async with aiohttp.ClientSession() as session:
                try:
                    json = await self.get_json(
                        session, f"https://ps2.fisu.pw/api/population/?world={choice}"
                    )
                    results = json["result"][0]
                    embed = discord.Embed(
                        title=f"Current population for {capital_server}:",
                        colour=discord.Colour.teal(),
                        description=f"**Terran Republic**: {results['tr']}\n**New Conglomerate**: {results['nc']}\n**Vanu Sovereignty**: {results['vs']}\n**Nanite Systems Operative**: {results['ns']}",
                    )
                    await ctx.send(embed=embed)
                except aiohttp.ClientResponseError as err:
                    logger.debug(
                        f"An error occurred collecting population data for {server}: {err}."
                    )
                    await ctx.send(
                        f"An error occurred retrieveing population data for {server}."
                    )
        else:
            logger.debug(f"Unknown server {server}.")
            await ctx.send(f"Unknown server {server}.")

    @commands.command()
    async def playerinfo(self, ctx: commands.Context, player_name: str):
        """
        Retrieve information for a Planetside 2 player.

        :param player_name: The name of the player to retrieve information for.
        """
        async with auraxium.Client() as client:
            try:
                player = await client.get_by_name(auraxium.ps2.Character, player_name)
            except ValueError as err:
                logger.debug(f"An error occurred looking up player {player_name}: {err}. Most likely they don't exist.")
                ctx.send(f"Player {player_name} not found.")
                break
            player_faction = await player.faction()
            player_outfit = await player.outfit()
            player_online = await player.is_online()
            if player_online:
                colour = discord.Colour.green()
            else:
                colour = discord.Colour.red()
            player_stats = f"""**Faction**: {player_faction}
**Outfit**: {player_outfit}
**Currently playing**: {player_online}
**Battle rank**: {player.data.battle_rank.value}
**A.S.P rank**: {player.data.prestige_level}
**Created**: {player.data.times.creation_date}
**Last login**: {player.data.times.last_login_date}
**Minutes played**: {player.data.times.minutes_played}
**Certs earned**: {player.data.certs.earned_points}
            """
            embed = discord.Embed(title=f"{player.data.name.first}'s Stats:", description=player_stats, colour=colour)

    @commands.command()
    async def outfitstats(self, ctx: commands.Context, outfit: str = "redmist"):
        """"""
        pass
