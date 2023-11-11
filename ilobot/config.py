import os

from dotenv import load_dotenv

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
load_dotenv(f"{__location__}/../.env")
DEBUG = int(os.getenv("DEBUG", "1"))
DB_NAME = os.getenv("DB_NAME", "ilobot")
PLATFORM = os.getenv("PLATFORM", "common-gen5")

# Minimum requirements
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
assert DISCORD_TOKEN, "You need to specify discord token"
DISCORD_CHANNEL = int(os.getenv("DISCORD_CHANNEL", "0"))
assert DISCORD_CHANNEL != 0, "You need to specify discord channel"
GUILD_ID = int(os.getenv("GUILD_ID", ""))
assert GUILD_ID, "You need to specify discord guild id"
CLUB_ID = os.getenv("CLUB_ID", "")
assert CLUB_ID, "You need to specify club id"


API_KEY = os.getenv("GIPHY_API_KEY")

OPEN_API = os.getenv("OPEN_API")
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-3.5-turbo")

CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
OAUTH = os.getenv("TWITCH_OAUTH", "")
STREAMERS = os.getenv("TWITCH_STREAMERS", "")
TWITCH_CHANNEL = os.getenv("TWITCH_CHANNEL")

TUMBLR_KEY = os.getenv("TUMBLR_KEY")
TUMBLR_SECRET = os.getenv("TUMBLR_SECRET")
TUMBLR_OAUTH_KEY = os.getenv("TUMBLR_OAUTH_KEY")
TUMBLR_OAUTH_SECRET = os.getenv("TUMBLR_OAUTH_SECRET")
TUMBLR_BLOG = os.getenv("TUMBLR_BLOG")
