import json
import os

import falcon
import falcon.asgi
import uvicorn
from dotenv import load_dotenv

from ilobot import calculations, data_service, db_mongo
from ilobot.extra.chatgpt import chatify_data
from ilobot.extra.format import format_game_data

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
load_dotenv(f"{__location__}/../.env")
API_KEY = os.getenv("OWN_API_KEY", "")
assert len(API_KEY) > 10, "You need to set proper api key for server"


class AuthMiddleware:
    async def process_request_async(self, req, resp):
        token = req.get_header("Authorization")

        if token is None:
            description = "Please provide an auth token as part of the request."

            raise falcon.HTTPUnauthorized(
                title="Auth token required",
                description=description,
            )

        if not self._token_is_valid(token):
            description = (
                "The provided auth token is not valid. "
                "Please request a new token and try again."
            )

            raise falcon.HTTPUnauthorized(
                title="Authentication required",
                description=description,
            )

    def _token_is_valid(self, token):
        return token == API_KEY


class SimpleAuthMiddleware:
    async def process_request_async(self, req, resp):
        token = req.get_param("password")

        if token != "ilopisara":
            raise falcon.HTTPUnauthorized(title="Authentication required")


# Falcon follows the REST architectural style, meaning (among
# other things) that you think in terms of resources and state
# transitions, which map to HTTP verbs.
class MatchesMarkdownResource:
    async def on_get(self, req, resp):
        """Handles GET requests"""
        resp.status = falcon.HTTP_200  # This is the default status
        resp.content_type = falcon.MEDIA_TEXT  # Default is JSON, so override
        games = await db_mongo.get_sorted_matches("timestamp")

        resp.text = ""
        for game in games:
            cleaned_game = chatify_data(game, skip_player_names=True)
            title = str(data_service.format_result(game))
            resp.text += format_game_data(cleaned_game, title)
            if "summary" in game:
                resp.text += game["summary"] + "\n"
            resp.text += "\n\n"


class MatchesResource:
    async def on_get(self, req, resp):
        limit = 10000
        if "limit" in req.params:
            limit = int(req.params["limit"])
        matches = await db_mongo.get_sorted_matches("timestamp")
        for m in matches:
            del m["_id"]
        resp.media = matches[:limit]


class WinsResources:
    async def on_get(self, req, resp):
        matches = await db_mongo.find_matches_by_club_id()
        result = calculations.win_percentages_by_hour(matches)
        resp.content_type = falcon.MEDIA_TEXT  # Default is JSON, so override
        resp.text = calculations.text_for_win_percentage_by_hour(result)


app = falcon.asgi.App(
    # middleware=[AuthMiddleware()],
    middleware=[SimpleAuthMiddleware()],
)

matches_resource = MatchesResource()
app.add_route("/matches", matches_resource)

winpct_resource = WinsResources()
app.add_route("/winpct", winpct_resource)

matches_md_resource = MatchesMarkdownResource()
app.add_route("/matchesmd", matches_md_resource)


if __name__ == "__main__":
    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=False)
