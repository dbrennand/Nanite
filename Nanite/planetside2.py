"""Planetside 2 bot cog.
"""
# Config imports
from .config import DEFAULT_PS2_WORLD

# Library imports
import discord
import typing
import aiohttp
import auraxium
from loguru import logger


class Planetside2(discord.ext.commands.Bot):
    """
    Class for Nanite's Planetside 2 Cog.

    Groups Planetside 2 related bot commands.
    """

    def __init__(self, bot: discord.ext.commands.Bot) -> None:
        """
        Initalisation function for Planetside 2 class.
        """
        self.bot = bot
        self.COLOUR = discord.Colour().teal()
        self.API_URL = "https://ps2.fisu.pw/api"

    # Private functions

    async def _get_world_id(self, world_name: str) -> typing.Tuple[int, None]:
        """Get the ID for a Planetside 2 world.

        [API documentation](https://ps2.fisu.pw/api/population/)

        Args:
            world_name (str): The name of the Planetside 2 world to obtain the ID for.

        Returns:
            typing.Tuple[int, None]: An integer representing the ID of the Planetside 2 world (if found), otherwise, returns None.
        """
        # Declare world dict
        worlds = {
            "connery": 1,
            "miller": 10,
            "cobalt": 13,
            "emerald": 17,
            "jaeger": 19,
            "apex": 24,
            "solTech": 40,
        }
        # Get the world ID from the world name
        world_id = worlds.get(world_name.lower(), None)
        logger.debug(f"World name: {world_name}, ID: {world_id}")
        return world_id

    async def _get_json(
        self, session: aiohttp.ClientSession, sub_resource: str
    ) -> dict:
        """Get a JSON payload from an API endpoint.

        Args:
            session (aiohttp.ClientSession): A reuseable aiohttp.ClientSession object to make HTTP requests.
            sub_resource (str): The sub resource of the API to retrieve JSON data from.

        Returns:
            dict: A dictionary object containing the JSON response (if any).
        """
        endpoint = f"{self.API_URL}/{sub_resource}"
        logger.debug(f"Getting JSON response from endpoint: {endpoint}")
        async with session.get(endpoint, raise_for_status=True) as resp:
            return await resp.json()

    async def _create_embed(
        self,
        title: str,
        description: str,
        colour: discord.Colour,
        thumbnail_url: str = None,
    ) -> discord.Embed:
        """Creates a Discord Embed object to send in in a Discord message.

        Args:
            title (str): The title of the discord.Embed object.
            description (str): The description of the discord.Embed object.
            colour (discord.Colour): A discord.Colour object to apply to the discord.Embed object.
            thumbnail_url (str, optional): The URL to provide as the thumbnail for the discord.Embed object.

        Returns:
            discord.Embed: A discord.Embed object.
        """
        return discord.Embed(
            title=title, description=description, colour=colour
        ).set_thumbnail(thumbnail_url)

    # Events and commands

    @discord.ext.commands.command()
    async def population(
        self,
        ctx: discord.ext.commands.Context,
        world: str = DEFAULT_PS2_WORLD,
    ) -> None:
        """Get current population data for a Planetside 2 world.

        [API documentation](https://ps2.fisu.pw/api/population/).

        Args:
            ctx (discord.ext.commands.Context): Represents the context in which a command is being invoked under.
            world (str, optional): The Planetside 2 world to get current population data for. Defaults to DEFAULT_PS2_WORLD.
        """
        logger.info(f"Getting population data for world: {world}")
        # Get world ID
        world_id = await self._get_world_id(world_name=world)
        if world_id:
            async with aiohttp.ClientSession() as session:
                try:
                    # Get JSON response
                    json = await self._get_json(
                        session=session, sub_resource=f"population/?world={world_id}"
                    )
                    # Get population data from JSON response
                    population_data = json["result"][0]
                    # Create Embed object
                    embed = await self._create_embed(
                        title=f"Current population data for: {world.capitalize()}",
                        description=f"**TR**: {population_data['tr']}\n**NC**: {population_data['nc']}\n**VS**: {population_data['vs']}\n**NSO**: {population_data['ns']}",
                        colour=self.COLOUR,
                    )
                    await ctx.send(embed=embed)
                except Exception as err:
                    logger.error(
                        f"Failed to get current population data for world: {world}, ID: {world_id}.\n{err}"
                    )
                    await ctx.send(
                        f"Failed to get current population data for world: {world}, ID: {world_id}"
                    )
        else:
            logger.warning(f"World: {world} unknown.")
            await ctx.send(f"World: {world} unknown.")

    @discord.ext.commands.command()
    async def pi(self, ctx: discord.ext.commands.Context, player_name: str) -> None:
        """
        Get information for a Planetside 2 player.

        Args:
            ctx (discord.ext.commands.Context): Represents the context in which a command is being invoked under.
            player_name (str): The name of the Planetside 2 player to get information for.
        """
        logger.info(f"Getting information for player: {player_name}")
        async with auraxium.Client() as client:
            try:
                # Get Character object
                player = await client.get_by_name(auraxium.ps2.Character, player_name)
                # Calculate hours played
                player_hours_played = round(
                    (int(player.data.times.minutes_played) / 60), 2
                )
                # Get player's world information
                player_world = await player.world()
                # Get player's faction information
                player_faction = await player.faction()
                # Get player's outfit information
                player_outfit = await player.outfit()
                # Get player's online status information
                player_online_status = await player.is_online()
                # Get player's total deaths
                # Profile ID 0 = global
                player_weapon_deaths = await player.stat(
                    stat_name="weapon_deaths", profile_id="0"
                )
                player_total_deaths = player_weapon_deaths[0]["value_forever"]
                # Get player's total kills
                player_kills = await player.stat_by_faction(
                    stat_name="weapon_kills", profile_id="0"
                )
                # Calculate total kill count
                player_total_kills = (
                    int(player_kills[0]["value_forever_vs"])
                    + int(player_kills[0]["value_forever_nc"])
                    + int(player_kills[0]["value_forever_tr"])
                )
                # Calculate KPH
                player_kph = round((player_total_kills / player_hours_played), 2)
                # Calculate KDR
                player_kdr = round(player_total_kills / int(player_total_deaths), 2)
                # Get player's total score
                player_score = await player.stat_history(stat_name="score")
                player_total_score = player_score[0]["all_time"]
                # Calculate SPM
                player_spm = round(
                    int(player_total_score) / int(player.times.minutes_played), 2
                )
                # Get player's total headshots
                player_hs = await player.stat_by_faction(
                    stat_name="weapon_headshots", profile_id="0"
                )
                # Calculate total headshot count
                player_hs_total = (
                    int(player_hs[0]["value_forever_vs"])
                    + int(player_hs[0]["value_forever_nc"])
                    + int(player_hs[0]["value_forever_tr"])
                )
                # Calculate HSR
                player_hsr = round((player_hs_total / player_total_kills) * 100, 2)
            except Exception as err:
                logger.error(
                    f"Failed to get player information for: {player_name}.\n{err}"
                )
                ctx.send(f"Failed to get player information for: {player_name}")
                return
        # Build faction image URL
        faction_image_url = (
            f"https://census.daybreakgames.com{player_faction.data.image_path}"
        )
        # Build embed message containing player information
        player_info = f"""
**Server**
{player_world}

**Outfit**
{player_outfit}

**Battle Rank (Prestige)**
{player.data.battle_rank.value} ({player.data.prestige_level})

**Total Kills**    **Total Deaths**    **Total Score**
{player_total_kills}    {player_total_deaths}    {player_total_score}

**KDR**    **SPM**    **HSR**    **KPH**
{player_kdr}    {player_spm}    {player_hsr}%    {player_kph}

**Currently Online**
{player_online_status}

**Last Login**
{player.data.times.last_login_date}

**Playtime Hours (Minutes)**
{player_hours_played} ({player.data.times.minutes_played})

**Total Certs Earned**
{player.data.certs.earned_points}

**Created**
{player.data.times.creation_date}
        """
        # Create embed
        embed = await self._create_embed(
            title=f"{player.data.name.first}'s Information",
            description=player_info,
            colour=self.COLOUR,
            thumbnail_url=faction_image_url,
        )
        await ctx.send(embed=embed)

    @discord.ext.commands.command()
    async def oi(self, ctx: discord.ext.commands.Context, outfit_tag: str) -> None:
        """
        Get information for a Planetside 2 outfit.

        Args:
            ctx (discord.ext.commands.Context): Represents the context in which a command is being invoked under.
            outfit_tag (str): The name of the Planetside 2 outfit to get information for.
        """
        logger.info(f"Getting information for outfit: {outfit_tag}")
        async with auraxium.Client() as client:
            try:
                # Retrieve outfit info
                outfit = await auraxium.ps2.Outfit.get_by_tag(
                    outfit_tag.capitalize(), client
                )
                # Retrieve outfit leader
                outfit_leader = await client.get_by_id(
                    auraxium.ps2.Character, outfit.data.leader_character_id
                )
            except Exception as err:
                logger.error(
                    f"Failed to get outfit information for outfit tag: {outfit_tag}.\n{err}"
                )
                ctx.send(
                    f"Failed to get outfit information for outfit tag: {outfit_tag}."
                )
                return
        # Create outfit info
        outfit_info = f"""**Outfit name**: {outfit.data.name}
**Creation Date**: {outfit.data.time_created_date}
**Member Count**: {outfit.data.member_count}
**Outfit Leader**: {outfit_leader}
        """
        # Create embed
        embed = await self._create_embed(
            title=f"Outfit Information for {outfit_tag.capitalize()}:",
            description=outfit_info,
            colour=self.COLOUR,
        )
        await ctx.send(embed=embed)
