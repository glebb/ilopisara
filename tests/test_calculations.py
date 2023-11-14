# pylint: disable=C0413
import json
import os

import pytest

from ilobot import calculations
from ilobot.db_utils import enrich_match
from ilobot.helpers import GAMETYPE

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
with open(f"{__location__}/matches.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    enriched_matches = [enrich_match(match, GAMETYPE.REGULARSEASON) for match in data]


@pytest.mark.asyncio
async def test_win_percentage_by_hours():
    result = calculations.win_percentages_by_hour(enriched_matches)[0]
    assert result.hour == 22
    assert result.wins == 0
    assert result.total_games == 1


def test_win_percentage_by_player_by_position():
    result = calculations.wins_by_player_by_position(enriched_matches)
    assert result["bodhi-FIN"]["defenseMen"].wins == 2
    assert result["bodhi-FIN"]["defenseMen"].total_games == 4
    assert result["bodhi-FIN"]["defenseMen"].win_percentage() == 50
