# pylint: disable=C0413
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ilobot.base_logger import logger
from ilobot.db_utils import enrich_match
from ilobot.extra import chatgpt
from ilobot.helpers import GAMETYPE

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

with open(f"{__location__}/matches.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    enriched_match = enrich_match(data[0], GAMETYPE.REGULARSEASON)

def test_clean_up_data():
    game = chatgpt.clean_up_data(enriched_match)
    logger.info(json.dumps(game))


def test_chat_is_generated():
    summary = chatgpt.write_gpt_summary(enriched_match)
    logger.info(summary)
    assert len(summary) > 1000
