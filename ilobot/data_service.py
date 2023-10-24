from dataclasses import fields
from datetime import datetime
from typing import List, Tuple

import pytz
from dacite import from_dict

from ilobot import helpers, jsonmap
from ilobot.models import Match, MemberRecord, Record, Result

filters = {
    1: "goalie",
    2: "skater",
    3: "xfactor",
}


def find(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return None


def format_result(match_raw: dict) -> Result:
    if isinstance(match_raw, dict):
        match = from_dict(data_class=Match, data=match_raw)
    else:
        match = match_raw
    timestamp = int(match.timestamp)
    score_time = (
        datetime.fromtimestamp(timestamp)
        .astimezone(pytz.timezone("Europe/Helsinki"))
        .strftime("%d.%m. %H:%M")
    )
    opponent_id = match.clubs[helpers.CLUB_ID].opponentClubId
    opponent_name = (
        match.clubs[opponent_id].details.name
        if match.clubs[opponent_id].details
        else "???"
    )
    score_teams = match.clubs[helpers.CLUB_ID].details.name + " vs " + opponent_name
    score_result = match.clubs[helpers.CLUB_ID].scoreString
    return Result(
        mark=helpers.get_match_mark(match),
        date_and_time=score_time,
        score=score_teams + " " + score_result,
        game_type=helpers.get_match_type_mark(match),
        match_id=match.matchId,
        summary=match.summary,
        match_type=match.clubs[helpers.CLUB_ID].get_match_type(),
    )


def format_stats(stats, stats_filter=None):
    message = ""
    if stats_filter:
        stats_filter = filters[stats_filter]
    for key, value in sorted(stats.items()):
        stat = None
        key = jsonmap.get_name(key)
        if stats_filter and key.startswith(stats_filter.lower()):
            stat = key + ": " + value
        elif not stats_filter:
            if (
                not key.startswith("skater")
                and not key.startswith("goalie")
                and not key.startswith("xfactor")
            ):
                stat = key + ": " + value
        if stat:
            message += stat + "\n"
    if message:
        return message


def _match_details(match_dict: dict):
    match = from_dict(data_class=Match, data=match_dict)
    players = ""
    for team_id in (match.opponent.id, helpers.CLUB_ID):
        players += f"\n**{match.clubs[team_id].details.name}**\n"
        for _, player in sorted(
            match.players[team_id].items(),
            key=lambda p: int(p[1].skgoals) + int(p[1].skassists),
            reverse=True,
        ):
            points = (
                f" {float(player.glsavepct) * 100:5.2f}%"
                if player.position == "goalie"
                else f" {player.skgoals} + {player.skassists}"
            )
            players += (
                f"** {player.position[0].upper()} {player.playername}: {points} **"
            )
            if team_id != helpers.CLUB_ID:
                players += "\n"
                continue
            players += "\n> ```"
            if player.position == "goalie":
                players += "saves:" + player.glsaves + ", "
                players += "breakaway save %:"
                players += (
                    f"{float(player.glbrksavepct) * 100:5.2f}%, "
                    if player.glbrkshots != "0"
                    else "100.00, "
                )
                players += "breakaways:" + player.glbrkshots + ", "
                players += "penaltyshot save %:"
                players += (
                    f"{float(player.glpensavepct) * 100:5.2f}%, "
                    if player.glpenshots != "0"
                    else "100.00, "
                )
                players += "penaltyshots:" + player.glpenshots + ", "
                players += "shots:" + player.glshots + ", "
            else:
                players += "shots:" + player.skshots + ", "
                players += "hits:" + player.skhits + ", "
                players += "blocked shots:" + player.skbs + ", "
                players += "giweaways:" + player.skgiveaways + ", "
                players += "takeaways:" + player.sktakeaways + ", "
                players += "pass attempts:" + player.skpassattempts + ", "
                players += "pass %:" + player.skpasspct + ", "
                players += "possession:" + player.skpossession + ", "
                players += "deflections:" + player.skdeflections + ", "
                players += "interceptions:" + player.skinterceptions + ", "
                players += "penalties:" + player.skpim + "m"
            if player.position.upper() == "CENTER":
                players += (
                    f", fow:{player.skfow}, fol:{player.skfol}, fopct: {player.skfopct}"
                )
            players += "```\n"
    return players


def match_result(match: dict) -> Tuple[Result, str]:
    return format_result(match), _match_details(match)


def top_stats(members_raw: List[dict], stats_filter: str, per_game=False):
    members = map(lambda m: from_dict(data_class=MemberRecord, data=m), members_raw)
    per_game_text = " per game" if per_game else ""
    key = jsonmap.get_key(stats_filter, jsonmap.names)
    reply = f"Top {stats_filter}\n```"
    try:
        for member in sorted(
            members,
            key=lambda m: float(getattr(m, key))
            if not per_game
            else float(getattr(m, key)) / float(m.skgp),
            reverse=True,
        ):
            value = getattr(member, key)
            if per_game:
                value = str(round(float(getattr(member, key)) / float(member.skgp), 2))
            reply += "" + member.name + " " + value + per_game_text + "\n"
    except (TypeError, ValueError):
        for member in sorted(members, key=lambda m: getattr(m, key), reverse=True):
            value = getattr(member, key)
            reply += member.name + " " + value + "\n"
    except KeyError:
        reply = ""
    if reply:
        reply += "```"
        return reply


def _should_update_record(existing_record, new_record):
    return (not existing_record) or float(new_record.stats_value) > float(
        existing_record.stats_value
    )


def _matches_existing_record(new_record: Record, existing_record: Record | None):
    if existing_record:
        return float(new_record.stats_value) == float(existing_record.stats_value)
    return False


def game_record(
    matches: List[dict], stats_filter: str, player_name=None, position=None
) -> List[Record]:
    stats_key = jsonmap.get_key(stats_filter, jsonmap.match)
    records: List[Record] = []
    for raw_match in matches:
        match = from_dict(data_class=Match, data=raw_match)
        for _, player_data in match.players[helpers.CLUB_ID].items():
            if stats_key in [field.name for field in fields(player_data)]:
                # if we are looking for a specific player records...
                if player_name and player_data.playername != player_name:
                    continue
                if position and player_data.position != position:
                    continue
                current_record = records[0] if len(records) > 0 else None

                new_record = Record(
                    player_data, match, stats_key, getattr(player_data, stats_key)
                )
                if _should_update_record(current_record, new_record):
                    records.clear()
                    records.append(new_record)
                elif _matches_existing_record(new_record, current_record):
                    records.append(new_record)

    if records:
        return records
    return []


def team_record(team):
    if not team:
        return None
    key = list(team.keys())[0]
    reply = ""
    if key:
        record = list(map(int, team[key]["record"].split("-")))
        number_of_games = sum(record)
        if number_of_games == 0:
            percentages = [0, 0, 0]
        else:
            percentages = [round(x / number_of_games * 100, 1) for x in record]
        reply += "Team: " + team[key]["name"] + "\n```"
        reply += (
            "record: "
            + team[key]["record"]
            + f" | {'% / '.join(list(map(str, percentages)))}%\n"
        )
        reply += "points: " + team[key]["rankingPoints"] + "\n"
        reply += "star level: " + team[key]["starLevel"] + "\n"
        reply += "current division: " + str(team[key]["currentDivision"]) + "\n"
        games = (
            int(team[key]["wins"])
            + int(team[key]["losses"])
            + int(team[key]["ties"])
            + int(team[key]["otl"])
        )
        if games > 0:
            goals_per_game = +int(team[key]["goals"]) / games
            goals_against_per_game = +int(team[key]["goalsAgainst"]) / games
        else:
            goals_per_game = 0
            goals_against_per_game = 0
        reply += f"goals per game: {goals_per_game:.2f}\n"
        reply += f"goals against per game: {goals_against_per_game:.2f}"
        reply += "```"
    if reply:
        return reply


if __name__ == "__main__":
    import json

    f = open(
        "tests/members.json",
        encoding="utf-8",
    )
    _members = json.load(f)
    f.close()

    f = open(
        "tests/matches.json",
        encoding="utf-8",
    )
    _matches = json.load(f)
    f.close()

    f = open(
        "tests/team.json",
        encoding="utf-8",
    )
    _team = json.load(f)
    f.close()

    # print(format_stats(members['members'][0], None))
    # print(format_result(matches[0]))
    # print(match_details(matches[1]))
    # print(top_stats(members['members'], 'skater goals'))
    # print(team_record(team))
    print(len(game_record(_matches, "xca dsfgsd gfsd")))
