from typing import List

import data_service
import db_mongo
import helpers
import jsonmap
from base_logger import logger
from data import api


async def results(club_id=None, game_type=None) -> List[data_service.Result]:
    matches = await db_mongo.find_matches_by_club_id(club_id, game_type)
    results = []
    for i in range(0, len(matches))[-20:]:
        results.append(data_service.format_result(matches[i]))
    return results


async def match(match_id):
    matches = await db_mongo.find_match_by_id(match_id)
    if matches:
        return data_service.match_result(matches[0])


async def member_stats(name, stats_filter=None, send_dm=False):
    members = api.get_members()
    member = api.get_member(name)
    reply = ""
    public_reply = "No stats available."
    index = data_service.find(members, "name", name)
    if index is not None:
        stats = members[index]
        reply = (
            f"Stats for {name} / {member['skplayername']}:\n"
            + data_service.format_stats(stats, stats_filter)
        )
        public_reply = (
            f"**{name} / {member['skplayername']}**\n"
            + "```Record: "
            + members[index]["record"]
            + "\nPoints: "
            + members[index]["points"]
            + "\nSkater win percentage: "
            + members[index]["skwinpct"]
            + "\nPoints per game: "
            + members[index]["skpointspg"]
            + "\nPass percentage: "
            + members[index]["skpasspct"]
            + "\nPenaltyshot percentage: "
            + members[index]["skpenaltyshotpct"]
            + "\nHits per game: "
            + members[index]["skhitspg"]
        )
        if int(members[index]["glgp"]) > 0:
            public_reply += (
                "\nGoalie games: "
                + members[index]["glgp"]
                + "\nGoal against average: "
                + members[index]["glgaa"]
                + "\nSave percentage: "
                + members[index]["glsavepct"]
            )

        public_reply += "```"

    logger.info(send_dm)
    if send_dm:
        public_reply += "Rest of the stats delivered by DM.\n"
    return_matches = []
    if member:
        matches = await db_mongo.find_matches_for_player(member["blazeId"])
        if matches:
            public_reply += "\nLatest games: \n"
            for i in range(0, len(matches))[-10:]:
                public_reply += (
                    data_service.format_result(matches[i]).discord_print() + "\n"
                )
                return_matches.append(matches[i])

    return reply, public_reply, [data_service.format_result(x) for x in return_matches]


async def game_record(stats_filter, player_name=None, position=None, team_stats=None):
    result = ""
    if team_stats:
        if team_stats in jsonmap.club_stats.keys():
            data_set = "clubs"
            key = jsonmap.club_stats.get(team_stats)
        else:
            data_set = "aggregate"
            key = jsonmap.get_key(team_stats, jsonmap.match)
        query = f"{data_set}.{helpers.CLUB_ID}.{key}"
        matches = await db_mongo.get_sorted_matches(query)
        index = 0
        for match in matches:
            if (
                match[data_set][helpers.CLUB_ID][key]
                < matches[0][data_set][helpers.CLUB_ID][key]
            ):
                break
            index += 1
        result = (
            f"Team {team_stats} record: {matches[0][data_set][helpers.CLUB_ID][key]}\n"
        )
        for match in matches[:index]:
            result += data_service.format_result(match).discord_print() + "\n"
        return result, [data_service.format_result(x) for x in matches[:index]]

    matches = await db_mongo.find_matches_by_club_id(player_name=player_name)
    return_matches = []
    temp = " ".join(stats_filter)
    records = data_service.game_record(
        matches, temp, player_name=player_name, position=position, team_stats=team_stats
    )
    if records:
        result = f"Single game record for {temp}"
        if player_name:
            result += f" for {player_name}"
        if position:
            result += f" as a {position}"

        result += "\n"
        for record in records[:10]:
            result += data_service.format_result(record.match).discord_print() + "\n"
            result += (
                record.player["position"][0].upper()
                + ": "
                + record.player["playername"]
                + ": "
            )
            result += str(record.stats_value) + " " + temp + "\n"
            return_matches.append(record.match)
    return result, [data_service.format_result(x) for x in return_matches]


async def team_record(name, platform):
    result_string = ""
    temp = api.get_team_record(name, platform)
    record = data_service.team_record(temp)
    matches = []
    if record:
        result_string += record + "\n"
        club_id = list(temp.keys())[0]
        members = api.get_members(club_id)
        if club_id != helpers.CLUB_ID:
            db_matches = await db_mongo.find_matches_by_club_id(versusClubId=club_id)
            if db_matches:
                matches = [data_service.format_result(x) for x in db_matches]
        top_stats = data_service.top_stats(members, "points per game")
        if top_stats:
            top_reply = top_stats
        else:
            top_reply = "\n" + "No top stats available"
        result_string += top_reply
    return result_string, matches
