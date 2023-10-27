from typing import Callable, List

import nextcord
from nextcord.ext import commands

from ilobot import command_service, data_service, db_mongo, helpers, jsonmap
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
        guild_ids=[helpers.GUILD_ID], description="Display team overview"
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
        platform = platform if platform is not None else helpers.PLATFORM
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
        guild_ids=[helpers.GUILD_ID],
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
    ):
        await interaction.response.defer()
        matches = await command_service.results(None, game_type)
        if len(matches) > 0:
            response = "\n".join([line.discord_print() for line in matches])
            await self.matches_dropdown(response, matches, interaction)
        else:
            await interaction.followup.send("No results found")

    @nextcord.slash_command(
        guild_ids=[helpers.GUILD_ID], description="Display match details"
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
        guild_ids=[helpers.GUILD_ID], description="Rank players by stat"
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
        guild_ids=[helpers.GUILD_ID], description="Display single player stats"
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
        send_dm: bool = nextcord.SlashOption(
            name="send_dm",
            required=False,
        ),
    ):
        await interaction.response.defer()
        response, public, matches = await command_service.member_stats(
            name, stats_filter, send_dm
        )
        response = "No results found" if not response else response
        if len(matches) > 0:
            await self.matches_dropdown(public, matches, interaction)
        else:
            await interaction.followup.send(public[:1999])
        if send_dm:
            assert interaction.user
            await interaction.user.send(response[:1999])

    @nextcord.slash_command(
        guild_ids=[helpers.GUILD_ID],
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
                "skater giweaways",
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
    ):
        await interaction.response.defer()
        response, matches = await command_service.game_record(
            [stats_name], player_name, position, team_stats
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
            await db_mongo.update_matches(helpers.CLUB_ID, helpers.PLATFORM)

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
