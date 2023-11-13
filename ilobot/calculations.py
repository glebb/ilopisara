import asyncio
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import List

import pytz

from ilobot import db_mongo
from ilobot.base_logger import logger


@dataclass
class WinsByHourPercentage:
    hour: int
    wins: int
    total_games: int

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


def print_win_percentage_by_hour(
    win_percentages_by_hour_result: List[WinsByHourPercentage],
):
    print("Win percentages by hour")
    print("Hour\tGP\tWin %")
    games = 0
    for item in sorted(
        win_percentages_by_hour_result,
        key=lambda w: w.hour,
    ):
        games += item.total_games
        print(f"{item.hour}\t{item.total_games}\t{item.win_percentage():.2f}%")
    print(f"Total games: {games}")


async def main():
    data = await db_mongo.find_matches_by_club_id()
    print_win_percentage_by_hour(win_percentages_by_hour(data))


if __name__ == "__main__":
    asyncio.run(main())
