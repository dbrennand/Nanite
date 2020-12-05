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

    async def get_server_id(self, server_name: str) -> int:
        """
        Retrieve the ID for a Planetside 2 server.

        [API documentation](https://ps2.fisu.pw/api/territory/)

        :param server_name: The name of the Planetside 2 server to obtain the ID for.
        :returns: A int representing the ID of the Planetside 2 server if found, otherwise, returns None.
        """
        # Declare server dict
        servers = {
            "connery": 1,
            "miller": 10,
            "cobalt": 13,
            "emerald": 17,
            "jaeger": 19,
            "apex": 24,
            "solTech": 40,
        }
        return servers.get(server_name.lower(), None)

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
        # Obtain server ID
        server_id = await self.get_server_id(server)
        if server_id:
            async with aiohttp.ClientSession() as session:
                try:
                    json = await self.get_json(
                        session,
                        f"https://ps2.fisu.pw/api/population/?world={server_id}",
                    )
                    results = json["result"][0]
                    embed = discord.Embed(
                        title=f"Current population for {server.capitalize()}:",
                        colour=discord.Colour.teal(),
                        description=f"**Terran Republic**: {results['tr']}\n**New Conglomerate**: {results['nc']}\n**Vanu Sovereignty**: {results['vs']}\n**Nanite Systems Operative**: {results['ns']}",
                    )
                    await ctx.send(embed=embed)
                except: # TODO: Find out what specific error occurs here
                    logger.debug(
                        f"An error occurred collecting population data for {server}."
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
                # Obtain general player info
                player = await client.get_by_name(auraxium.ps2.Character, player_name)
            except ValueError as err:
                logger.debug(
                    f"An error occurred looking up player {player_name}: {err}. Most likely they don't exist."
                )
                ctx.send(f"Player {player_name} not found.")
                return
            # Obtain player faction info
            player_faction = await player.faction()
            # Build faction image URL
            faction_image_url = (
                f"https://census.daybreakgames.com{player_faction.data.image_path}"
            )
            # Obtain player outfit info
            player_outfit = await player.outfit()
            # Obtain player online status info
            player_online = await player.is_online()
            # Change colour of discord embed depending wheather the player is online or not
            if player_online:
                colour = discord.Colour.green()
            else:
                colour = discord.Colour.red()
            # Build embed message containing player info
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
            # Build embed and send
            embed = discord.Embed(
                title=f"{player.data.name.first}'s Stats:",
                description=player_stats,
                colour=colour,
            ).set_thumbnail(url=faction_image_url)
            await ctx.send(embed=embed)

    @commands.command()
    async def outfitstats(self, ctx: commands.Context, outfit: str = "redmist"):
        """"""
        pass
