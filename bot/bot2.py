import os

import jsonmap
import command_service
import data_service
from base_logger import logger
from data import api
from dotenv import load_dotenv
from nextcord import Interaction, SlashOption
from nextcord.ext import commands

load_dotenv("../.env")
GUILD_ID = int(os.getenv("GUILD_ID"))
TOKEN = os.getenv("DISCORD_TOKEN")
CLUB_ID = os.getenv("CLUB_ID")

members = list(map(lambda x: x["name"], api.get_members()["members"]))

bot = commands.Bot()


@bot.slash_command(guild_ids=[GUILD_ID], description="Display team overview")
async def team(
    interaction: Interaction,
    name: str = SlashOption(
        name="name",
        description="Team name",
    ),
):
    response = await command_service.team_record(name)
    response = "No results found" if not response else response
    await interaction.response.send_message(response)


@bot.slash_command(
    guild_ids=[GUILD_ID], description="Display results for most rececnt matches"
)
async def results(
    interaction: Interaction,
):
    response = await command_service.results()
    response = "No results found" if not response else response
    await interaction.response.send_message(response)


@bot.slash_command(guild_ids=[GUILD_ID], description="Display match details")
async def match(
    interaction: Interaction,
    id: str = SlashOption(
        name="id",
        description="Match id",
    ),
):
    response = await command_service.match(id)
    response = "No results found" if not response else response
    await interaction.response.send_message(response)


@bot.slash_command(guild_ids=[GUILD_ID], description="Rank players by stat")
async def top(
    interaction: Interaction,
    stats_name: str = SlashOption(
        name="stats_name",
        description="Stats name (e.g. points)",
    ),
):
    members = api.get_members()["members"]
    response = data_service.top_stats(members, stats_name)
    response = "No results found" if not response else response
    await interaction.response.send_message(response)


@bot.slash_command(guild_ids=[GUILD_ID], description="Display single player stats")
async def player(
    interaction: Interaction,
    name: str = SlashOption(
        name="name",
        description="Player name",
    ),
    filter: int = SlashOption(
        name="filter",
        choices={"goalie": 1, "skater": 2, "xfactor": 3},
        required=False,
    ),
):
    response = await command_service.member_stats(name, filter)
    response = "No results found" if not response else response
    await interaction.response.send_message(response)


@bot.slash_command(guild_ids=[GUILD_ID], description="Display game record for a stat")
async def record(
    interaction: Interaction,
    stats_name: str = SlashOption(
        name="stats_name",
        description="Game specific record for a stat (e.g. goals)",
    ),
):
    response = await command_service.game_record([stats_name])
    response = "No results found" if not response else response
    await interaction.response.send_message(response[:1999])


@top.on_autocomplete("stats_name")
async def select_stats(interaction: Interaction, stats_name: str):
    if not stats_name:
        # send the full autocomplete list
        await interaction.response.send_autocomplete(list(jsonmap.names.values())[:25])
        return
    # send a list of nearest matches from the list of dog breeds
    get_near_stats = [
        stat
        for stat in list(jsonmap.names.values())
        if stats_name.lower() in stat.lower()
    ]
    await interaction.response.send_autocomplete(get_near_stats[:25])

@record.on_autocomplete("stats_name")
async def select_stats(interaction: Interaction, stats_name: str):
    if not stats_name:
        # send the full autocomplete list
        await interaction.response.send_autocomplete(list(jsonmap.match.values())[:25])
        return
    # send a list of nearest matches from the list of dog breeds
    get_near_stats = [
        stat
        for stat in list(jsonmap.match.values())
        if stats_name.lower() in stat.lower()
    ]
    await interaction.response.send_autocomplete(get_near_stats[:25])

@player.on_autocomplete("name")
async def select_player(interaction: Interaction, name: str):
    if not name:
        # send the full autocomplete list
        await interaction.response.send_autocomplete(members[:25])
        return
    # send a list of nearest matches from the list of dog breeds
    get_near_members = [
        n
        for n in list(members)
        if name.lower() in n.lower()
    ]
    await interaction.response.send_autocomplete(get_near_members[:25])

bot.run(TOKEN)