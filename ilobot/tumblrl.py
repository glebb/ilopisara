import pytumblr

from ilobot.base_logger import logger
from ilobot.config import (  # type: ignore
    TUMBLR_BLOG,
    TUMBLR_KEY,
    TUMBLR_OAUTH_KEY,
    TUMBLR_OAUTH_SECRET,
    TUMBLR_SECRET,
)

tumblr_client = pytumblr.TumblrRestClient(
    TUMBLR_KEY, TUMBLR_SECRET, TUMBLR_OAUTH_KEY, TUMBLR_OAUTH_SECRET
)


def post(raw_text: str, title=None, tags=None):
    resp = None
    if not tags:
        tags = []
    try:
        resp = tumblr_client.create_text(
            TUMBLR_BLOG, body=raw_text.replace("\n", "<br />"), title=title, tags=tags
        )
    except Exception:
        logger.exception("TUMBLR error - couldn't post")
    return resp
