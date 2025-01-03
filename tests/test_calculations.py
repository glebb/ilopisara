# pylint: disable=C0413
import json
import os

import pytest

from ilobot import calculations
from ilobot.db_utils import enrich_match
from ilobot.helpers import GAMETYPE

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
with open(f"{__location__}/matches_24.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    enriched_matches = {
        "2380": [enrich_match(match, GAMETYPE.REGULARSEASON, "2380") for match in data]
    }


@pytest.mark.asyncio
async def test_win_percentage_by_hours():
    result = calculations.win_percentages_by_hour(enriched_matches)[0]
    assert result.hour == 22
    assert result.wins == 0
    assert result.total_games == 1


def test_win_percentage_by_player_by_position():
    result = calculations.wins_by_player_by_position(enriched_matches)
    assert result["bodhi-FIN"]["LD (3vs3)"].wins == 2
    assert result["bodhi-FIN"]["LD (3vs3)"].total_games == 4
    assert result["bodhi-FIN"]["LD (3vs3)"].win_percentage() == 50


def test_win_percentage_by_loadout_by_position():
    result = calculations.wins_by_loadout_by_position(enriched_matches)
    assert result["LD (3vs3)"]["Puck Moving Defenseman"].wins == 2
    assert result["LD (3vs3)"]["Puck Moving Defenseman"].total_games == 4
    assert result["LD (3vs3)"]["Puck Moving Defenseman"].win_percentage() == 50


def test_win_percentage_by_loadout_lineup():
    result = calculations.wins_by_loadout_lineup(enriched_matches)
    lineup = "LD: Puck Moving Defenseman\nC: Power Forward"
    assert result["3vs3"][lineup].wins == 2
    assert result["3vs3"][lineup].total_games == 4
    assert result["3vs3"][lineup].win_percentage() == 50
