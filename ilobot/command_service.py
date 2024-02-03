from typing import List

from ilobot import config, data_service, db_mongo, helpers, jsonmap
from ilobot.base_logger import logger
from ilobot.data import api


async def results(club_id=None, game_type=None) -> List[data_service.Result]:
    data = []
    matches = await db_mongo.find_matches_by_club_id(club_id, game_type)
    if matches:
        for i in range(0, len(matches))[-20:]:
            data.append(data_service.format_result(matches[i]))
    return data


async def match(match_id):
    matches = await db_mongo.find_match_by_id(match_id)
    if matches:
        return data_service.match_result(matches[0])


def get_as_number(value):
    if isinstance(value, int) or isinstance(value, float):
        return value
    if "." in value:
        try:
            return float(value)
        except ValueError:
            return None
    else:
        try:
            return int(value)
        except ValueError:
            return None


async def member_stats(name, source, stats_filter=None):
    member = api.get_member(name)
    members = api.get_members()
    if source:
        wins = 0
        losses = 0
        ovt_losses = 0
        goalie_games = 0
        skater_games = 0
        member_id = member["blazeId"]
        player_name = member["skplayername"]
        matches = await db_mongo.find_matches_for_player(member_id)
        stats = {}
        for match in matches:
            model = data_service.convert_match(match)
            match_type = model.clubs[config.CLUB_ID].get_match_type().value
            if match_type != source:
                continue
            if match["win"]:
                wins += 1
            else:
                if helpers.is_overtime(model):
                    ovt_losses += 1
                else:
                    losses += 1
            for key, value in match["players"][config.CLUB_ID][member_id].items():
                if key.startswith("sk") or key.startswith("gl"):
                    temp_value = (
                        get_as_number(value)
                        if get_as_number(value) is not None
                        else value
                    )
                    if key not in stats:
                        stats[key] = temp_value
                    elif get_as_number(value):
                        stats[key] = stats[key] + temp_value
            if match["players"][config.CLUB_ID][member_id]["posSorted"] == "0":
                goalie_games += 1
            else:
                skater_games += 1

        for key in stats:
            if key == "glgaa" and goalie_games > 0:
                stats[key] = round(stats["glga"] / goalie_games, 2)
            if key == "glsavepct" and goalie_games > 0:
                stats[key] = round(stats["glsaves"] / stats["glshots"], 2)
            if key == "skpasspct" and stats["skpassattempts"] > 0:
                stats[key] = round(stats["skpasses"] / stats["skpassattempts"] * 100, 2)
            if key == "skfopct" and stats["skfopct"] > 0:
                stats[key] = round(
                    (stats["skfow"] / (stats["skfow"] + stats["skfol"])) * 100, 2
                )
            if key == "skshotonnetpct" and stats["skshotonnetpct"] > 0:
                stats[key] = round(stats["skshots"] / stats["skshotattempts"] * 100, 2)

            if key == "skshotpct" and stats["skshots"] > 0:
                stats[key] = round(stats["skgoals"] / stats["skshots"] * 100, 2)

            if key == "glsavepct" and stats["glshots"] > 0:
                stats[key] = round(stats["glsaves"] / stats["glshots"] * 100, 2)
            if key == "glbrksavepct" and stats["glbrkshots"] > 0:
                stats[key] = round(stats["glbrksaves"] / stats["glbrkshots"] * 100, 2)
            if key == "glpensavepct" and stats["glpenshots"] > 0:
                stats[key] = round(stats["glpensaves"] / stats["glpenshots"] * 100, 2)

        stats["record"] = f"{wins}-{losses}-{ovt_losses}"
        stats["glgp"] = goalie_games
        stats["skgp"] = skater_games
        stats["skpointspg"] = (
            round(stats["skpoints"] / skater_games, 2) if skater_games > 0 else 0
        )
        stats["skhitspg"] = (
            round(stats["skhits"] / skater_games, 2) if skater_games > 0 else 0
        )
        stats["skplayername"] = player_name
        stats["blazeId"] = member_id
        stats["skpoints"] = stats["skgoals"] + stats["skassists"]
    else:
        index = data_service.find(members, "name", name)
        if index is not None:
            stats = members[index]

    reply = ""
    public_reply = "No stats available."
    if stats:
        if not source:
            source = ""
        reply = (
            f"Stats for {name} / {member['skplayername']} {source}\n"
            + data_service.format_stats(stats, stats_filter)
        )
        public_reply = (
            f"**{name} / {member['skplayername']} {source}**\n"
            + "```Record: "
            + str(stats["record"])
            + "\nPoints: "
            + str(stats["skpoints"])
            + "\nPoints per game: "
            + str(stats["skpointspg"])
            + "\nPass percentage: "
            + str(stats["skpasspct"])
            + "\nHits per game: "
            + str(stats["skhitspg"])
        )
        if int(stats["glgp"]) > 0:
            public_reply += (
                "\nGoalie games: "
                + str(stats["glgp"])
                + "\nGoal against average: "
                + str(stats["glgaa"])
                + "\nSave percentage: "
                + str(stats["glsavepct"])
            )

        public_reply += "```"

    return_matches = []
    if member:
        matches = await db_mongo.find_matches_for_player(member["blazeId"])
        if matches:
            if source:
                matches = [
                    x
                    for x in matches
                    if data_service.convert_match(x)
                    .clubs[config.CLUB_ID]
                    .get_match_type()
                    .value
                    == source
                ]
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
        if team_stats in jsonmap.club_stats:
            data_set = "clubs"
            key = jsonmap.club_stats.get(team_stats)
        else:
            data_set = "aggregate"
            key = jsonmap.get_key(team_stats, jsonmap.match)
        query = f"{data_set}.{config.CLUB_ID}.{key}"
        matches = await db_mongo.get_sorted_matches(query)
        index = 0
        for raw_match in matches:
            if float(raw_match[data_set][config.CLUB_ID][key]) < float(
                matches[0][data_set][config.CLUB_ID][key]
            ):
                break
            index += 1
        result = (
            f"Team {team_stats} record: {matches[0][data_set][config.CLUB_ID][key]}\n"
        )
        for raw_match in matches[:index]:
            result += data_service.format_result(raw_match).discord_print() + "\n"
        return result, [data_service.format_result(x) for x in matches[:index]]

    matches = await db_mongo.find_matches_by_club_id(player_name=player_name)
    return_matches = []
    records = []
    if matches:
        temp = " ".join(stats_filter)
        records = data_service.game_record(
            matches, temp, player_name=player_name, position=position
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
                record.player.position[0].upper()
                + ": "
                + record.player.playername
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
        if club_id != config.CLUB_ID:
            db_matches = await db_mongo.find_matches_by_club_id(versus_club_id=club_id)
            if db_matches:
                matches = [data_service.format_result(x) for x in db_matches]
        top_stats = data_service.top_stats(members, "points per game")
        if top_stats:
            top_reply = top_stats
        else:
            top_reply = "\n" + "No top stats available"
        result_string += top_reply
    return result_string, matches
