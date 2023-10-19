import pytumblr

from ilobot.helpers import (
    TUMBLR_KEY,
    TUMBLR_OAUTH_KEY,
    TUMBLR_OAUTH_SECRET,
    TUMBLR_SECRET,
)

tumblr_client = pytumblr.TumblrRestClient(
    TUMBLR_KEY, TUMBLR_SECRET, TUMBLR_OAUTH_KEY, TUMBLR_OAUTH_SECRET
)
