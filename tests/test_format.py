import pytest

from ilobot import db_mongo
from ilobot.base_logger import logger
from ilobot.extra.chatgpt import chatify_data
from ilobot.extra.format import format_game_data


@pytest.mark.asyncio
async def test_clean_up_data():
    games = await db_mongo.get_latest_match(2)
    for game in games:
        cleaned_game = chatify_data(game)
        logger.info(format_game_data(cleaned_game))
