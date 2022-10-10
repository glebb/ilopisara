from dataclasses import dataclass
from datetime import datetime

import helpers
import jsonmap
import pytz

filters = {
    1: "goalie",
    2: "skater",
    3: "xfactor",
}


@dataclass
class Result:
    mark: str
    date_and_time: str
    score: str
    game_type: str
    match_id: str

    def __str__(self):
        return (
            self.mark
            + " "
            + self.date_and_time
            + " "
            + self.score
            + " "
            + self.game_type
            + " // "
            + self.match_id
        )


def find(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return None


def format_result(match):
    ts = int(match["timestamp"])
    score_time = datetime.fromtimestamp(ts)
    score_time = score_time.astimezone(pytz.timezone("Europe/Helsinki")).strftime(
        "%d.%m. %H:%M"
    )
    opponentId = match["clubs"][helpers.CLUB_ID]["opponentClubId"]
    opponentName = (
        match["clubs"][opponentId]["details"]["name"]
        if match["clubs"][opponentId]["details"] != None
        else "???"
    )
    score_teams = (
        match["clubs"][helpers.CLUB_ID]["details"]["name"] + " - " + opponentName
    )
    score_result = match["clubs"][helpers.CLUB_ID]["scoreString"]
    return Result(
        mark=helpers.get_match_mark(match),
        date_and_time=score_time,
        score=score_teams + " " + score_result,
        game_type=helpers.get_match_type_mark(match),
        match_id=match["matchId"],
    )


def format_stats(stats, stats_filter=None):
    message = ""
    if stats_filter:
        stats_filter = filters[stats_filter]
    for k, v in sorted(stats.items()):
        stat = None
        key = jsonmap.get_name(k)
        if stats_filter and key.startswith(stats_filter.lower()):
            stat = key + ": " + v
        elif not stats_filter:
            if (
                not key.startswith("skater")
                and not key.startswith("goalie")
                and not key.startswith("xfactor")
            ):
                stat = key + ": " + v
        if stat:
            message += stat + "\n"
    if message:
        return message


def _match_details(match):
    players = ""
    for _, p in sorted(
        match["players"][helpers.CLUB_ID].items(),
        key=lambda p: int(p[1]["skgoals"]) + int(p[1]["skassists"]),
        reverse=True,
    ):
        players += p["position"][0].upper() + ": " + p["playername"] + " "
        if p["position"] == "goalie":
            players += "save %:" + p["glsavepct"] + ", "
            players += "saves:" + p["glsaves"] + ", "
            players += "shots:" + p["glshots"] + "\n"
        else:
            players += p["skgoals"] + "+" + p["skassists"] + "\n> "
            players += "shots:" + p["skshots"] + ", "
            players += "hits:" + p["skhits"] + ", "
            players += "blocked shots:" + p["skbs"] + ", "
            players += "giweaways:" + p["skgiveaways"] + ", "
            players += "takeaways:" + p["sktakeaways"] + ", "
            players += "pass%:" + p["skpasspct"] + ", "
            players += "p/m:" + p["skplusmin"] + ", "
            players += "penalties:" + p["skpim"] + "m\n"
    return players


def match_result(match):
    return format_result(match), _match_details(match)


def top_stats(members, stats_filter):
    key = jsonmap.get_key(stats_filter, jsonmap.names)
    reply = f"Top {stats_filter}\n"
    try:
        for member in sorted(members, key=lambda m: float(m[key]), reverse=True):
            reply += member["name"] + " " + member[key] + "\n"
    except (TypeError, ValueError):
        for member in sorted(members, key=lambda m: m[key], reverse=True):
            reply += member["name"] + " " + member[key] + "\n"
    except KeyError:
        reply = ""
    if reply:
        return reply


def game_record(matches, stats_filter, player_name=None):
    key = jsonmap.get_key(stats_filter, jsonmap.match)
    ref_matches = []
    for match in matches:
        for playerid, player_data in match["players"][helpers.CLUB_ID].items():
            if player_name and player_data["playername"] != player_name:
                continue
            try:
                if (not ref_matches and key in player_data) or float(
                    player_data[key]
                ) > float(
                    ref_matches[0][1]["players"][helpers.CLUB_ID][ref_matches[0][0]][
                        key
                    ]
                ):
                    ref_matches.clear()
                    ref_matches.append([playerid, match, key])
                elif float(player_data[key]) == float(
                    ref_matches[0][1]["players"][helpers.CLUB_ID][ref_matches[0][0]][
                        key
                    ]
                ):
                    ref_matches.append([playerid, match, key])
            except (TypeError, ValueError):
                pass
            except KeyError:
                pass

    if ref_matches:
        return ref_matches


def team_record(team):
    if not team:
        return None
    key = list(team.keys())[0]
    reply = ""
    if key:
        reply += "Team: " + team[key]["name"] + "\n"
        reply += "points: " + team[key]["rankingPoints"] + "\n"
        reply += "star level: " + team[key]["starLevel"] + "\n"
        reply += "record: " + team[key]["record"] + "\n"
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
        reply += "goals per game: " + "{:.2f}".format(goals_per_game) + "\n"
        reply += "goals against per game: " + "{:.2f}".format(goals_against_per_game)
    if reply:
        return reply


if __name__ == "__main__":
    import json

    f = open(
        "tests/members.json",
    )
    _members = json.load(f)
    f.close()

    f = open(
        "tests/matches.json",
    )
    _matches = json.load(f)
    f.close()

    f = open(
        "tests/team.json",
    )
    _team = json.load(f)
    f.close()

    # print(format_stats(members['members'][0], None))
    # print(format_result(matches[0]))
    # print(match_details(matches[1]))
    # print(top_stats(members['members'], 'skater goals'))
    # print(team_record(team))
    print(len(game_record(_matches, "xca dsfgsd gfsd")))
