import asyncio
from typing import Callable, List

import nextcord
from nextcord.ext import commands

import ilobot.config
from ilobot import (
    calculations,
    command_service,
    data_service,
    db_mongo,
    helpers,
    jsonmap,
)
from ilobot.base_logger import logger
from ilobot.bot import Bot
from ilobot.data import api

from .models import Result


class GameDetails(nextcord.ui.Select):
    def __init__(self, options, match_callback: Callable):
        self.match_callback = match_callback
        super().__init__(
            placeholder="Choose game to show details",
            options=options,
        )

    async def callback(self, interaction: nextcord.Interaction):
        await self.match_callback(interaction, self.values[0])


class DropdownView(nextcord.ui.View):
    def __init__(self, details, timeout):
        super().__init__(timeout=timeout)
        self.add_item(details)


class ApplicationCommandCog(commands.Cog):
    MEMBERS = tuple(map(lambda x: x["name"], api.get_members()))
    MEMBERS = tuple(sorted(MEMBERS, key=str.casefold))

    def __init__(self, bot: Bot):
        self.bot = bot

    async def matches_dropdown(
        self, response, matches: List[Result], interaction: nextcord.Interaction
    ):
        options = []
        cleaned = {}
        match: Result
        for match in matches:
            if match.match_id not in cleaned:
                cleaned[match.match_id] = match
        for match in cleaned.values():
            label = match.date_and_time + " " + match.score
            options.append(nextcord.SelectOption(label=label, value=match.match_id))
        view = DropdownView(GameDetails(options, self.match), None)
        await interaction.followup.send(response[:1999], view=view)

    @nextcord.slash_command(
        guild_ids=[ilobot.config.GUILD_ID], description="Display team overview"
    )
    async def team(
        self,
        interaction: nextcord.Interaction,
        name: str = nextcord.SlashOption(
            name="name",
            description="Team name",
        ),
        platform: str = nextcord.SlashOption(
            name="platform",
            choices=helpers.PLATFORMS,
            required=False,
            description="Optionally select platform",
        ),
    ):
        await interaction.response.defer()
        platform = platform if platform is not None else ilobot.config.PLATFORM
        try:
            response, matches = await command_service.team_record(name, platform)
        except:
            logger.error(f"Error in team command for {name} {platform}")
            response = "Error"
            await interaction.followup.send(response[:1999])
            raise
        response = "No results found" if not response else response
        if len(matches) > 0:
            response += "\nMatch history:\n"
            response += "\n".join([line.discord_print() for line in matches])
            await self.matches_dropdown(response, matches, interaction)
        else:
            await interaction.followup.send(response[:1999])

    @nextcord.slash_command(
        guild_ids=[ilobot.config.GUILD_ID], description="Display data analytics"
    )
    async def analytics(
        self,
        interaction: nextcord.Interaction,
        name: str = nextcord.SlashOption(
            choices={
                "Win percentage by hour": "winpct",
                "Win percentage by player by position": "winpctposplr",
                "Win percentage by position by loadout": "winpctposloadout",
                "Win percentage by lineup": "winpctlineup",
            },
            required=True,
        ),
        db: str = nextcord.SlashOption(
            choices={
                "All-time": "",
                "NHL 24": ilobot.config.DB_NAME,
                "NHL 23" if ilobot.config.DB_NAME_23 else "NHL 24": (
                    ilobot.config.DB_NAME_23
                    if ilobot.config.DB_NAME_23
                    else ilobot.config.DB_NAME
                ),
            },
            required=False,
        ),
        reverse: bool = nextcord.SlashOption(
            name="reverse", required=False, description="Reverse", default=False
        ),
    ):
        await interaction.response.defer()
        response = "Error"
        title = "Uknown"
        db_name = ilobot.config.DB_NAME
        club_id = ilobot.config.CLUB_ID
        matches = {}
        if db and ilobot.config.DB_NAME_23 and ilobot.config.CLUB_ID_23:
            db_name = db
            club_id = (
                ilobot.config.CLUB_ID
                if db == ilobot.config.DB_NAME
                else ilobot.config.CLUB_ID_23
            )
        if not db and (ilobot.config.DB_NAME_23 and ilobot.config.CLUB_ID_23):
            matches[ilobot.config.CLUB_ID] = await db_mongo.find_matches_by_club_id()
            matches[ilobot.config.CLUB_ID_23] = await db_mongo.find_matches_by_club_id(
                db_name=ilobot.config.DB_NAME_23
            )
            title = "All-time\n"

        else:
            matches[club_id] = await db_mongo.find_matches_by_club_id(db_name=db_name)
            title = "NHL 24\n" if db_name == ilobot.config.DB_NAME else "NHL 23\n"
        if name == "winpct":
            response = calculations.text_for_win_percentage_by_hour(
                calculations.win_percentages_by_hour(matches)
            )
        if name == "winpctposplr":
            response = calculations.text_for_win_percentage_by_player_by_position(
                calculations.wins_by_player_by_position(matches)
            )
        if name == "winpctposloadout":
            response = calculations.text_for_win_percentage_by_player_by_position(
                calculations.wins_by_loadout_by_position(matches)
            )
        if name == "winpctlineup":
            response = calculations.text_for_wins_by_loadout_lineup(
                calculations.wins_by_loadout_lineup(matches), reverse=reverse
            )

        response = title + response
        if len(response) >= 1800:
            indx = response[1800:].find("\n") + 1800
            await interaction.followup.send(f"```\n{response[:indx]}```")
            await interaction.followup.send(f"```\n{response[indx:]}```")
        else:
            await interaction.followup.send(f"```\n{response[:1990]}```")

    @nextcord.slash_command(
        guild_ids=[ilobot.config.GUILD_ID],
        description="Display results for most rececnt matches",
    )
    async def results(
        self,
        interaction: nextcord.Interaction,
        game_type: str = nextcord.SlashOption(
            name="game_type",
            choices={g_type.name: g_type.value for g_type in helpers.GAMETYPE},
            required=False,
            description="Optionally limit matches by game type",
        ),
        match_type: str = nextcord.SlashOption(
            name="match_type",
            choices=("3vs3", "6vs6"),
            required=False,
        ),
    ):
        await interaction.response.defer()
        matches = await command_service.results(None, game_type, match_type)
        if len(matches) > 0:
            response = "\n".join([line.discord_print() for line in matches])
            await self.matches_dropdown(response, matches, interaction)
        else:
            await interaction.followup.send("No results found")

    @nextcord.slash_command(
        guild_ids=[ilobot.config.GUILD_ID], description="Display match details"
    )
    async def match(
        self,
        interaction: nextcord.Interaction,
        match_id: str = nextcord.SlashOption(
            name="match_id",
            description="Match id",
        ),
    ):
        await interaction.response.defer()
        response, details = await command_service.match(match_id)
        if response:
            response = response.discord_print() + "\n" + details
        response = "No results found" if not response else response
        await interaction.followup.send(response[:1999])

    @nextcord.slash_command(
        guild_ids=[ilobot.config.GUILD_ID], description="Rank players by stat"
    )
    async def top(
        self,
        interaction: nextcord.Interaction,
        stats_name: str = nextcord.SlashOption(
            name="stats_name",
            description="Stats name (e.g. points)",
        ),
        per_game: bool = nextcord.SlashOption(
            name="per_game",
            required=False,
            description="Calcluate value per game?",
        ),
    ):
        await interaction.response.defer()
        members = api.get_members()
        response = data_service.top_stats(members, stats_name, per_game)
        response = "No results found" if not response else response
        await interaction.followup.send(response[:1999])

    @nextcord.slash_command(
        guild_ids=[ilobot.config.GUILD_ID], description="Display single player stats"
    )
    async def player(
        self,
        interaction: nextcord.Interaction,
        name: str = nextcord.SlashOption(
            name="name", choices={name: name for name in MEMBERS}
        ),
        stats_filter: int = nextcord.SlashOption(
            name="stats_filter",
            choices={"goalie": 1, "skater": 2, "xfactor": 3},
            required=False,
        ),
        source: str = nextcord.SlashOption(
            name="source",
            choices=("3vs3", "6vs6"),
            required=False,
            description="Get data from online or database",
        ),
        position: str = nextcord.SlashOption(
            name="position",
            choices={value: key for key, value in helpers.POSITIONS.items()},
            required=False,
            description="Player position (requires also source)",
        ),
    ):
        await interaction.response.defer()
        response, public, matches = await command_service.member_stats(
            name, source, stats_filter, position
        )
        response = "No results found" if not response else response
        if len(matches) > 0:
            await self.matches_dropdown(public, matches, interaction)
        else:
            await interaction.followup.send(public[:1999])
        assert interaction.user
        if len(response) >= 1800:
            indx = 0
            while indx < len(response):
                temp = response[indx + 1800 :].find("\n") + 1800 + indx
                await interaction.user.send(f"```\n{response[indx:temp]}```")
                indx = temp
        else:
            await interaction.user.send(f"```\n{response[:1990]}```")

    @nextcord.slash_command(
        guild_ids=[ilobot.config.GUILD_ID],
        description="Display single game record for a stat",
    )
    async def record(
        self,
        interaction: nextcord.Interaction,
        stats_name: str = nextcord.SlashOption(
            name="stats_name",
            required=False,
            description="Game specific record for a stat (e.g. goals) in a single game",
        ),
        team_stats: str = nextcord.SlashOption(
            name="team_stats",
            choices=list(jsonmap.club_stats.keys())
            + [
                "skater shots",
                "skater hits",
                "skater blocked shots",
                "skater giveaways",
                "skater takeaways",
                "skater pass attempts",
                "skater penalty minutes",
                "goalie saves",
                "goalie breakaway saves",
                "goalie penalty shot saves",
                "goalie penalty shots",
                "goalie shots",
            ],
            required=False,
            description="Team record for single game",
        ),
        player_name: str = nextcord.SlashOption(
            name="player_name",
            choices={name: name for name in MEMBERS},
            required=False,
            description="Optionally check record for specific player",
        ),
        position: str = nextcord.SlashOption(
            name="position",
            choices=["center", "leftWing", "rightWing", "defenseMen", "goalie"],
            required=False,
            description="Optionally choose player position",
        ),
        match_type: str = nextcord.SlashOption(
            name="match_type",
            choices=("3vs3", "6vs6"),
            required=False,
        ),
    ):
        await interaction.response.defer()
        response, matches = await command_service.game_record(
            [stats_name], player_name, position, team_stats, match_type
        )
        response = "No results found" if not response else response
        if len(matches) > 0:
            await self.matches_dropdown(response, matches, interaction)
        else:
            await interaction.followup.send(response[:1999])

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        assert self.bot.user
        if self.bot.user != message.author and self.bot.user.mentioned_in(message):
            logger.info("udpate")
            await db_mongo.update_matches(ilobot.config.CLUB_ID, ilobot.config.PLATFORM)

    @top.on_autocomplete("stats_name")
    async def select_stats(self, interaction: nextcord.Interaction, stats_name: str):
        if not stats_name:
            await interaction.response.send_autocomplete(
                list(jsonmap.names.values())[:25]
            )
            return
        get_near_stats = [
            stat
            for stat in list(jsonmap.names.values())
            if stats_name.lower() in stat.lower()
        ]
        await interaction.response.send_autocomplete(get_near_stats[:25])

    @record.on_autocomplete("stats_name")
    async def select_stats_for_record(
        self, interaction: nextcord.Interaction, stats_name: str
    ):
        if not stats_name:
            await interaction.response.send_autocomplete(
                list(jsonmap.match.values())[:25]
            )
            return
        get_near_stats = [
            stat
            for stat in list(jsonmap.match.values())
            if stats_name.lower() in stat.lower()
        ]
        await interaction.response.send_autocomplete(get_near_stats[:25])

    @team.on_autocomplete("name")
    async def select_teams(self, interaction: nextcord.Interaction, name: str):
        if not name:
            await interaction.response.send_autocomplete(self.bot.get_team_names())
            return
        get_near_names = [
            n for n in list(self.bot.all_teams) if n.lower().startswith(name.lower())
        ]
        await interaction.response.defer()
        await interaction.response.send_autocomplete(get_near_names[:25])
