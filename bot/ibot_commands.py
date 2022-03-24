import os
from dotenv import load_dotenv
import interactions
from data import api
import data_service

from ibot_services import (
    get_stats_choice_chunks,
    get_member_choices,
    get_match_stats_choice_chucnks,
)
import command_service
import asyncio
from extra import features, fb

client: interactions.Client = None

load_dotenv("../.env")
CLUB_ID = int(os.getenv("CLUB_ID"))
CHANNEL = int(os.getenv("DISCORD_CHANNEL"))


async def long_running_top(stat):
    members = api.get_members()["members"]
    result = data_service.top_stats(members, stat)
    if result:
        await client._http.send_message(CHANNEL, f"{result}")


def create_top_command(bot):
    stat_choice_chunks = get_stats_choice_chunks()
    top_command_options = []
    for i in range(0, len(stat_choice_chunks)):
        option = interactions.Option(
            name=f"stats{i+1}",
            description=f"stats{i+1}",
            type=interactions.OptionType.STRING,
            choices=stat_choice_chunks[i],
        )
        top_command_options.append(option)

    @bot.command(
        name="top",
        description="Top stats",
        options=top_command_options,
    )
    async def top(
        ctx: interactions.CommandContext,
        stats1="",
        stats2="",
        stats3="",
        stats4="",
        stats5="",
        stats6="",
        stats7="",
        stats8="",
        stats9="",
        stats10="",
    ):
        stat = (
            stats1
            or stats2
            or stats3
            or stats4
            or stats4
            or stats5
            or stats6
            or stats7
            or stats8
            or stats9
            or stats10
        )
        await ctx.send("Please wait...")
        asyncio.ensure_future(long_running_top(stat))

    for i in range(0, len(stat_choice_chunks)):

        @bot.autocomplete(command="top", name=f"stats{i+1}")
        async def autocomplete_choice_list(ctx, user_input: str = ""):
            await ctx.populate(stat_choice_chunks[i])


async def long_running_team(name):
    temp = api.get_team_record(name)
    team_record = data_service.team_record(temp)
    if team_record:
        await client._http.send_message(CHANNEL, team_record)
        clubId = list(temp.keys())[0]
        members = api.get_members(clubId)
        if features.firebase_enabled() and clubId != CLUB_ID:
            matches = fb.find_matches_by_club_id(clubId)
        else:
            matches = None
        top_stats = data_service.top_stats(members["members"], "points per game")
        if top_stats:
            top_reply = "---\n" + top_stats
        else:
            top_reply = "---\n" + "No top stats available"
        await client._http.send_message(CHANNEL, top_reply)
        match_results = command_service.match_results2(matches)
        await client._http.send_message(CHANNEL, match_results)
    else:
        await client._http.send_message(
            CHANNEL,
            "\nSomething went wrong. Try again after few minutes. Also check team name is correct: "
            + name,
        )


def create_team_command(bot):
    @bot.command(
        name="team",
        description="Stats for team",
        options=[
            interactions.Option(
                name="name",
                description="Team name",
                type=interactions.OptionType.STRING,
                required=True,
            ),
        ],
    )
    async def team(ctx: interactions.CommandContext, name=""):
        await ctx.send("Please wait...")
        asyncio.ensure_future(long_running_team(name))


async def long_running_matches(match_id):
    matches = await command_service.matches(match_id)
    await client._http.send_message(CHANNEL, matches)


def create_matches_command(bot):
    @bot.command(
        name="matches",
        description="Match history",
        options=[
            interactions.Option(
                name="match_id",
                description="match id",
                type=interactions.OptionType.STRING,
                required=False,
            ),
        ],
    )
    async def matches(ctx: interactions.CommandContext, match_id=""):
        await ctx.send("Please wait...")
        if match_id:
            match_id = ["", match_id]
        else:
            match_id = []
        asyncio.ensure_future(long_running_matches(match_id))


async def long_running_stats(ctx: interactions.CommandContext, player_name):
    reply = await command_service.member_stats(player_name)
    await ctx.author.send(reply)


def create_stats_command(bot):
    @bot.command(
        name="stats",
        description="Player stats",
        options=[
            interactions.Option(
                name="player_name",
                description="Player name",
                type=interactions.OptionType.STRING,
                required=True,
                choices=get_member_choices(),
            ),
        ],
    )
    async def stats(ctx: interactions.CommandContext, player_name=""):
        await ctx.send("Please wait...")
        if player_name:
            player_name = ["", player_name]
        else:
            player_name = []
        asyncio.ensure_future(long_running_stats(ctx, player_name))


async def long_running_record(stat):
    print(stat)
    result = await command_service.game_record([stat])
    await client._http.send_message(CHANNEL, result)


def create_record_command(bot):
    stat_choice_chunks = get_match_stats_choice_chucnks()
    command_options = []
    for i in range(0, len(stat_choice_chunks)):
        option = interactions.Option(
            name=f"rstats{i+1}",
            description=f"rstats{i+1}",
            type=interactions.OptionType.STRING,
            choices=stat_choice_chunks[i],
        )
        command_options.append(option)

    @bot.command(
        name="record",
        description="Game record",
        options=command_options,
    )
    async def record(
        ctx: interactions.CommandContext,
        rstats1="",
        rstats2="",
        rstats3="",
    ):
        stat = (
            rstats1
            or rstats2
            or rstats3
        )
        await ctx.send("Please wait...")
        asyncio.ensure_future(long_running_record(stat))
