import os

import command_service
import data_service
import db_mongo
import helpers
import jsonmap
from data import api
from dotenv import load_dotenv
from nextcord import Interaction, SlashOption
from nextcord.ext import commands, tasks

load_dotenv("../.env")
DISCORD_CHANNEL = int(os.getenv("DISCORD_CHANNEL"))
GUILD_ID = int(os.getenv("GUILD_ID"))
TOKEN = os.getenv("DISCORD_TOKEN")
CLUB_ID = os.getenv("CLUB_ID")

members = list(map(lambda x: x["name"], api.get_members()["members"]))
members = tuple(sorted(members, key=str.casefold))
team_name = api.get_team_info(CLUB_ID)[CLUB_ID]["name"]


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop.create_task(self.watch_db())
        self.all_teams = ()
        self.fetch_team_names.start()

    async def watch_db(self):
        await self.wait_until_ready()
        await db_mongo.watch(self.report_results)

    async def report_results(self, match):
        channel = self.get_channel(int(DISCORD_CHANNEL))
        result_string = data_service.match_result(match)
        if result_string:
            await channel.send(result_string)

    def get_team_names(self):
        short_list = list(self.all_teams[-24:])
        try:
            short_list.insert(0, short_list.pop(short_list.index(team_name)))
        except:
            short_list.insert(0, team_name)
        return tuple(short_list)

    @tasks.loop(minutes=10)
    async def fetch_team_names(self):
        self.all_teams = tuple(await db_mongo.get_known_team_names())


bot = Bot()


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
    await interaction.response.send_message(response[:1999])


@bot.slash_command(
    guild_ids=[GUILD_ID], description="Display results for most rececnt matches"
)
async def results(
    interaction: Interaction,
    game_type: str = SlashOption(
        name="game_type",
        choices={g_type.name: g_type.value for g_type in helpers.GAMETYPE},
        required=False,
        description="Optionally limit matches by game type",
    ),
):
    response = await command_service.results(None, game_type)
    response = "No results found" if not response else response
    await interaction.response.send_message(response[:1999])


@bot.slash_command(guild_ids=[GUILD_ID], description="Display match details")
async def match(
    interaction: Interaction,
    match_id: str = SlashOption(
        name="match_id",
        description="Match id",
    ),
):
    response = await command_service.match(match_id)
    response = "No results found" if not response else response
    await interaction.response.send_message(response[:1999])


@bot.slash_command(guild_ids=[GUILD_ID], description="Rank players by stat")
async def top(
    interaction: Interaction,
    stats_name: str = SlashOption(
        name="stats_name",
        description="Stats name (e.g. points)",
    ),
):
    online_members = api.get_members()["members"]
    response = data_service.top_stats(online_members, stats_name)
    response = "No results found" if not response else response
    await interaction.response.send_message(response[:1999])


@bot.slash_command(guild_ids=[GUILD_ID], description="Display single player stats")
async def player(
    interaction: Interaction,
    name: str = SlashOption(name="name", choices={name: name for name in members}),
    stats_filter: int = SlashOption(
        name="stats_filter",
        choices={"goalie": 1, "skater": 2, "xfactor": 3},
        required=False,
    ),
):
    response, public = await command_service.member_stats(name, stats_filter)
    response = "No results found" if not response else response
    await interaction.user.send(response[:1999])
    await interaction.response.send_message(public)


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
        await interaction.response.send_autocomplete(list(jsonmap.names.values())[:25])
        return
    get_near_stats = [
        stat
        for stat in list(jsonmap.names.values())
        if stats_name.lower() in stat.lower()
    ]
    await interaction.response.send_autocomplete(get_near_stats[:25])


@record.on_autocomplete("stats_name")
async def select_stats_for_record(interaction: Interaction, stats_name: str):
    if not stats_name:
        await interaction.response.send_autocomplete(list(jsonmap.match.values())[:25])
        return
    get_near_stats = [
        stat
        for stat in list(jsonmap.match.values())
        if stats_name.lower() in stat.lower()
    ]
    await interaction.response.send_autocomplete(get_near_stats[:25])


@team.on_autocomplete("name")
async def select_teams(interaction: Interaction, name: str):
    if not name:
        await interaction.response.send_autocomplete(bot.get_team_names())
        return
    get_near_names = [
        n for n in list(bot.all_teams) if n.lower().startswith(name.lower())
    ]
    await interaction.response.defer()
    await interaction.response.send_autocomplete(get_near_names[:25])


bot.run(TOKEN)
