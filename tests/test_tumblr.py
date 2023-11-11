# pylint: disable=C0413
import os

from ilobot import tumblrl
from ilobot.base_logger import logger
from ilobot.config import TUMBLR_BLOG

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def test_tumblr_post():
    resp = tumblrl.post("test", "title", ["#nhl24"])
    logger.info(resp)
    assert resp["state"] == "published"
    tumblrl.tumblr_client.delete_post(TUMBLR_BLOG, resp["id"])
