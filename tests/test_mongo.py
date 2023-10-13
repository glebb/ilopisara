import pytest

from ilobot import command_service, data_service, db_mongo
from ilobot.base_logger import logger


@pytest.mark.asyncio
async def test_get_latest_games():
    matches = [
        str(data_service.format_result(m)) for m in await db_mongo.get_latest_match(20)
    ]
    logger.info(matches)
