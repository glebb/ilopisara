import data_service
import db_mongo
import helpers
from data import api


async def results(club_id=None, game_type=None):
    matches = await db_mongo.find_matches_by_club_id(club_id, game_type)
    results = []
    for i in range(0, len(matches))[-20:]:
        results.append(data_service.format_result(matches[i]))
    return results


async def match(match_id):
    matches = await db_mongo.find_match_by_id(match_id)
    if matches:
        return data_service.match_result(matches[0])


async def member_stats(name, stats_filter=None):
    members = api.get_members()
    reply = ""
    public_reply = "No game history available."
    index = data_service.find(members, "name", name)
    if index:
        stats = members[index]
        reply = f"Stats for {name}:\n" + data_service.format_stats(stats, stats_filter)
        public_reply = (
            f"{name}\n"
            + "Record: "
            + members[index]["record"]
            + "\nRest of the stats delivered by DM."
        )
    member = api.get_member(name)
    return_matches = []
    if member:
        matches = await db_mongo.find_matches_for_player(member["blazeId"])
        if matches:
            public_reply += "\n\nLatest games: \n"
            for i in range(0, len(matches))[-10:]:
                public_reply += str(data_service.format_result(matches[i])) + "\n"
                return_matches.append(matches[i])

    return reply, public_reply, [data_service.format_result(x) for x in return_matches]


async def game_record(stats_filter, player_name=None):
    result = ""
    matches = await db_mongo.find_matches_by_club_id(player_name=player_name)
    return_matches = []
    temp = " ".join(stats_filter)
    records = data_service.game_record(matches, temp, player_name=player_name)
    if records:
        result = f"Single game record for {temp}"
        if player_name:
            result += f" for {player_name}"
        result += "\n"
        for record in records[:10]:
            result += str(data_service.format_result(record.match)) + "\n"
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
                matches = list(map(lambda x: data_service.format_result(x), db_matches))
        top_stats = data_service.top_stats(members, "points per game")
        if top_stats:
            top_reply = "---\n" + top_stats
        else:
            top_reply = "---\n" + "No top stats available"
        result_string += top_reply
    return result_string, matches
