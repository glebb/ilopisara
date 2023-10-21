# pylint: disable=C0413
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ilobot import data_service, db_mongo
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


@pytest.mark.asyncio
async def test_chat_is_generated():
    history = await db_mongo.get_latest_match(2)
    results = [(data_service.format_result(m).as_chatgpt_history()) for m in history]
    del history[0]["_id"]
    del history[0]["summary"]
    summary = await chatgpt.write_gpt_summary(history[0], results[1:])
    logger.info(history[0])
    logger.info(results[1])
    logger.info(summary)
    assert len(summary) > 1000
