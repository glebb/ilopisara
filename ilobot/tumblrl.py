import pytumblr

from ilobot.helpers import (
    TUMBLR_BLOG,
    TUMBLR_KEY,
    TUMBLR_OAUTH_KEY,
    TUMBLR_OAUTH_SECRET,
    TUMBLR_SECRET,
)

tumblr_client = pytumblr.TumblrRestClient(
    TUMBLR_KEY, TUMBLR_SECRET, TUMBLR_OAUTH_KEY, TUMBLR_OAUTH_SECRET
)


def post(raw_text: str, title=None, tags=[]):
    return tumblr_client.create_text(
        TUMBLR_BLOG, body=raw_text.replace("\n", "<br />"), title=title, tags=tags
    )
