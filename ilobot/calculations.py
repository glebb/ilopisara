import asyncio
from collections import Counter, OrderedDict
from dataclasses import dataclass
from datetime import datetime
from pprint import pformat, pprint
from typing import List

import pytz
from dacite import from_dict

from ilobot import data_service, db_mongo, helpers
from ilobot.base_logger import logger
from ilobot.config import CLUB_ID, CLUB_ID_23, DB_NAME_23
from ilobot.models import Match, MatchType


@dataclass
class WinsByHourPercentage:
    hour: int
    wins: int
    total_games: int

    def win_percentage(self):
        return self.wins / self.total_games * 100 if self.total_games > 0 else 0


@dataclass
class WinsByPosition:
    position: str
    wins: int = 0
    total_games: int = 0

    def win_percentage(self):
        return self.wins / self.total_games * 100 if self.total_games > 0 else 0


def win_percentages_by_hour(matches):
    hour_counter = Counter()
    win_counter = Counter()

    for db in matches:
        for row in matches[db]:
            hour = (
                datetime.fromtimestamp(int(row["timestamp"]))
                .astimezone(pytz.timezone("Europe/Helsinki"))
                .hour
            )

            hour_counter[hour] += 1
            if row["win"]:
                win_counter[hour] += 1

    result_by_hour = [
        WinsByHourPercentage(hour, win_counter[hour], hour_counter[hour])
        for hour in hour_counter
    ]
    return result_by_hour


def text_for_win_percentage_by_hour(
    win_percentages_by_hour_result: List[WinsByHourPercentage],
):
    text = ""
    text += "Win percentages by hour\n"
    text += f"{'Hour'.ljust(5)}\t{'GP'.rjust(4)}\t{'Win %'.rjust(7)}\n"
    games = 0
    for item in sorted(
        win_percentages_by_hour_result,
        key=lambda w: w.hour,
    ):
        games += item.total_games
        text += f"{str(item.hour).ljust(5)}\t{str(item.total_games).rjust(4)}\t{item.win_percentage():6.2f}%\n"
    text += f"Total games: {games}\n"
    return text


def wins_by_player_by_position(matches):
    players = {}
    for db in matches:
        for match in matches[db]:
            model = from_dict(data_class=Match, data=match)
            for _, player in model.players[db].items():
                if player.isGuest != "0":
                    continue
                name = player.playername
                position = f"{player.get_position()} ({model.clubs[db].get_match_type().value})"
                if name not in players:
                    players[name] = {}
                if position not in players[name]:
                    players[name][position] = WinsByPosition(position=position)
                if match["win"]:
                    players[name][position].wins += 1
                players[name][position].total_games += 1
    return sort_by_win_percentage(players)


def sort_by_win_percentage(data):
    sorted_data = {}
    for p_key, _ in data.items():
        sorted_data[p_key] = {}
        sorted_data[p_key] = dict(
            sorted(
                data[p_key].items(),
                key=lambda x: x[1].win_percentage(),
                reverse=True,
            )
        )
    return sorted_data


def wins_by_loadout_by_position(matches):
    loadouts = {}
    for db in matches:
        for match in matches[db]:
            model = data_service.convert_match(match)
            for _, player in model.players[db].items():
                if player.isGuest != "0":
                    continue
                name = helpers.LOADOUTS.get(player.loadout, player.loadout)
                position = f"{player.get_position()} ({model.clubs[db].get_match_type().value})"
                if position not in loadouts:
                    loadouts[position] = {}
                if name not in loadouts[position]:
                    loadouts[position][name] = WinsByPosition(position=position)
                if match["win"]:
                    loadouts[position][name].wins += 1
                loadouts[position][name].total_games += 1

    return sort_by_win_percentage(loadouts)


def wins_by_loadout_lineup(matches):
    lineups = {}
    for db in matches:
        for match in matches[db]:
            model = data_service.convert_match(match)
            match_type = model.clubs[db].get_match_type().value
            match_loadouts = []
            for _, player in model.players[db].items():
                if player.position == "goalie":
                    continue
                loadout = helpers.LOADOUTS.get(player.loadout, player.loadout)
                match_loadouts.append(
                    {
                        "position": player.get_position(),
                        "pos_sorted": player.posSorted,
                        "loadout": loadout,
                    }
                )
            sorted_lineups = sorted(match_loadouts, key=lambda x: x["pos_sorted"])
            lineup = ""
            for l in sorted_lineups:
                lineup += f"{l['position']}: {l['loadout']}\n"
            lineup = lineup.strip()
            if match_type not in lineups:
                lineups[match_type] = {}
            if lineup not in lineups[match_type]:
                lineups[match_type][lineup] = WinsByPosition(position=lineup)
            if match["win"]:
                lineups[match_type][lineup].wins += 1
            lineups[match_type][lineup].total_games += 1
    return sort_by_win_percentage(lineups)


def text_for_win_percentage_by_player_by_position(wins):
    text = f"{'Name'.ljust(22)}\t{'GP'.rjust(4)}\t{'Win %'.rjust(8)}\n"
    for player_name, player in wins.items():
        text += f"{player_name}\n"
        for position, data in player.items():
            text += f"{position.ljust(22)}\t{str(data.total_games).rjust(4)}\t{data.win_percentage():6.2f}%\n"
        text += "\n"
    return text


def text_for_wins_by_loadout_lineup(wins, limit=5, min_games=3, reverse=False):
    text = ""
    for match_type in wins.keys():
        logger.info(f"type {match_type} number of matches: {len(wins[match_type])}")
        min_games_limit = min_games
        if match_type == MatchType.THREE_ON_THREE.value:
            min_games_limit = min_games + 2
        elif len(wins[match_type]) > 100:
            min_games_limit = min_games + 2
        counter = 0
        text += f"Lineup win percentages {match_type} (min number of games {min_games_limit})\n"
        temp = (
            reversed(wins[match_type].items()) if reverse else wins[match_type].items()
        )
        for lineup, data in temp:
            if counter == limit:
                counter = 0
                break
            if data.total_games >= min_games_limit:
                counter += 1
                text += f"Total games: {str(data.total_games)}\tWin percetange: {data.win_percentage():6.2f}%\n{lineup}\n"
                text += "\n"
        text += "\n"

    return text


async def main():
    data = {}
    data[CLUB_ID] = await db_mongo.find_matches_by_club_id()
    data[CLUB_ID_23] = await db_mongo.find_matches_by_club_id(db_name=DB_NAME_23)
    print(text_for_win_percentage_by_hour(win_percentages_by_hour(data)))
    print(
        text_for_win_percentage_by_player_by_position(wins_by_player_by_position(data))
    )
    print(
        text_for_win_percentage_by_player_by_position(wins_by_loadout_by_position(data))
    )
    print(
        text_for_wins_by_loadout_lineup(
            wins_by_loadout_lineup(data), limit=1000, min_games=-1
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
