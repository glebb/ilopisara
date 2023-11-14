import asyncio
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pprint import pformat, pprint
from typing import List

import pytz
from dacite import from_dict

from ilobot import db_mongo
from ilobot.base_logger import logger
from ilobot.config import CLUB_ID
from ilobot.models import Match


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

    for row in matches:
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
    text += "Hour\tGames Played\tWin %\n"
    games = 0
    for item in sorted(
        win_percentages_by_hour_result,
        key=lambda w: w.hour,
    ):
        games += item.total_games
        text += f"{item.hour}\t{item.total_games}\t{item.win_percentage():.2f}%\n"
    text += f"Total games: {games}\n"
    return text


def wins_by_player_by_position(matches):
    players = {}
    for match in matches:
        model = from_dict(data_class=Match, data=match)
        for player_id, player in match["players"][CLUB_ID].items():
            if player["isGuest"] != "0":
                continue
            name = player["playername"]
            position = (
                f"{player['position']} ({model.clubs[CLUB_ID].get_match_type().value})"
            )
            if name not in players:
                players[name] = {}
            if position not in players[name]:
                # players[name][position] = {"wins": 0, "total_games": 0}
                players[name][position] = WinsByPosition(position=position)
            if match["win"]:
                players[name][position].wins += 1
            players[name][position].total_games += 1
    return players


def text_for_win_percentage_by_player_by_position(wins):
    logger.info(wins)
    text = ""
    for player_name, player in wins.items():
        text += f"{player_name}\n"
        text += f"\tposition\twin %\tgames played\n"
        for position, data in player.items():
            text += f"\t{position}\t{data.win_percentage():.2f}\t{data.total_games}\n"
    return text


async def main():
    data = await db_mongo.find_matches_by_club_id()
    print(text_for_win_percentage_by_hour(win_percentages_by_hour(data)))
    print(
        text_for_win_percentage_by_player_by_position(wins_by_player_by_position(data))
    )


if __name__ == "__main__":
    asyncio.run(main())
