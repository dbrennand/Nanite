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

    async def create_embed(
        self,
        title: str,
        description: str,
        colour: discord.Colour,
        thumbnail_url: str = None,
    ) -> discord.Embed:
        """
        Create a discord Embed object to send in in a discord message.

        :param title: The title of the embed.
        :param description: The description of the embed.
        :param colour: The colour to set the embed.
        :param thumbnail_url: The URL of the image to be used in the embed thumbnail.
        :returns: A discord.Embed object.
        """
        logger.debug("Creating discord Embed object.")
        return discord.Embed(
            title=title, description=description, colour=colour
        ).set_thumbnail(thumbnail_url)

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
        # Retrieve server ID
        server_id = await self.get_server_id(server)
        if server_id:
            async with aiohttp.ClientSession() as session:
                try:
                    json = await self.get_json(
                        session,
                        f"https://ps2.fisu.pw/api/population/?world={server_id}",
                    )
                    results = json["result"][0]
                    # Create embed
                    embed = await self.create_embed(
                        f"Current population for {server.capitalize()}:",
                        f"**Terran Republic**: {results['tr']}\n**New Conglomerate**: {results['nc']}\n**Vanu Sovereignty**: {results['vs']}\n**Nanite Systems Operative**: {results['ns']}",
                        discord.Colour.teal(),
                    )
                    await ctx.send(embed=embed)
                except:  # TODO: Find out what specific error occurs here
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
                # Retrieve general player info
                player = await client.get_by_name(auraxium.ps2.Character, player_name)
            except ValueError as err:
                logger.debug(
                    f"An error occurred looking up player {player_name}: {err}.\nMost likely they don't exist."
                )
                ctx.send(f"Player {player_name} not found.")
                return
            # Retrieve player faction info
            player_faction = await player.faction()
            # Build faction image URL
            faction_image_url = (
                f"https://census.daybreakgames.com{player_faction.data.image_path}"
            )
            # Retrieve player outfit info
            player_outfit = await player.outfit()
            # Retrieve player online status info
            player_online = await player.is_online()
            # Change colour of discord embed depending wheather the player is online or not
            if player_online:
                colour = discord.Colour.green()
            else:
                colour = discord.Colour.red()
            # Build embed message containing player info
            player_info = f"""**Faction**: {player_faction}
**Outfit**: {player_outfit}
**Currently playing**: {player_online}
**Battle rank**: {player.data.battle_rank.value}
**A.S.P rank**: {player.data.prestige_level}
**Created**: {player.data.times.creation_date}
**Last login**: {player.data.times.last_login_date}
**Minutes played**: {player.data.times.minutes_played}
**Certs earned**: {player.data.certs.earned_points}
            """
            # Create embed
            embed = await self.create_embed(
                f"{player.data.name.first}'s Information:",
                player_info,
                colour,
                faction_image_url,
            )
            await ctx.send(embed=embed)

    @commands.command()
    async def outfitinfo(self, ctx: commands.Context, outfit_tag: str = "RMIS"):
        """
        Retrieve information about a Planetside 2 outfit.

        :params outfit_tag: The tag of the Planetside 2 outfit.
        """
        async with auraxium.Client() as client:
            try:
                outfit = await auraxium.ps2.outfit.Outfit.get_by_tag(outfit_tag, client)
            except ValueError as err:
                logger.debug(
                    f"An error occurred looking up the outfit tag {outfit_tag}: {err}. Most likely the outfit doesn't exist."
                )
                ctx.send(f"Outfit {outfit_tag} not found.")
                return
            # Retrieve outfit leader
            outfit_leader = await client.get_by_id(
                auraxium.ps2.Character, outfit.data.leader_character_id
            )
        # Create outfit info
        outfit_info = f"""**Outfit name**: {outfit.data.name}
**Creation date**: {outfit.data.time_created_date}
**Member count**: {outfit.data.member_count}
**Outfit leader**: {outfit_leader}
        """
        # Create embed
        embed = await self.create_embed(
            "Outfit Information:", outfit_info, discord.Colour.teal()
        )
        await ctx.send(embed=embed)
