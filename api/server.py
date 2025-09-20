import os
import pprint

import falcon
import falcon.asgi
import markdown
import uvicorn
from dotenv import load_dotenv

from ilobot import calculations, data_service, db_mongo
from ilobot.base_logger import logger
from ilobot.extra.chatgpt import chatify_data
from ilobot.extra.format import format_game_data

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
load_dotenv(f"{__location__}/../.env")
API_KEY = os.getenv("OWN_API_KEY", "")
PWD = "ilopisara"
assert len(API_KEY) > 10, "You need to set proper api key for server"

html = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head><body>"""


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

        if token != PWD:
            raise falcon.HTTPUnauthorized(title="Authentication required")


# Falcon follows the REST architectural style, meaning (among
# other things) that you think in terms of resources and state
# transitions, which map to HTTP verbs.
class MatchesMarkdownResource:
    async def on_get(self, req, resp):
        """Handles GET requests"""
        resp.status = falcon.HTTP_200  # This is the default status
        resp.content_type = falcon.MEDIA_HTML  # Default is JSON, so override
        games = await db_mongo.get_sorted_matches("timestamp")
        text = ""
        for game in games:
            cleaned_game = chatify_data(game, skip_player_names=True)
            title = f"[{str(data_service.format_result(game))}](/match?id={game['matchId']}&password={PWD})"
            text += format_game_data(cleaned_game, title)
            if "summary" in game:
                text += game["summary"] + "\n"
            text += "\n\n"
        resp.text = html + markdown.markdown(text) + "</body></html>"


class MatchesResource:
    async def on_get(self, req, resp):
        limit = 10000
        if "limit" in req.params:
            limit = int(req.params["limit"])
        matches = await db_mongo.get_sorted_matches("timestamp")
        for m in matches:
            del m["_id"]
        resp.media = matches[:limit]


class MatchResource:
    async def on_get(self, req, resp):
        match_id = None
        if "id" in req.params:
            match_id = int(req.params["id"])
        try:
            match = await db_mongo.find_match_by_id(str(match_id))
        except Exception:
            logger.exception("Failed to find match")
            pass
        if not match or len(match) != 1:
            raise falcon.HTTPBadRequest(
                title="No match found",
            )
        resp.status = falcon.HTTP_200  # This is the default status
        resp.content_type = falcon.MEDIA_HTML  # Default is JSON, so override
        del match[0]["_id"]
        cleaned_game = chatify_data(match[0], skip_player_names=True)
        resp.text = (
            html + "<pre>" + pprint.pformat(cleaned_game) + "</pre></body></html>"
        )


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

match_resource = MatchResource()
app.add_route("/match", match_resource)


winpct_resource = WinsResources()
app.add_route("/winpct", winpct_resource)

matches_md_resource = MatchesMarkdownResource()
app.add_route("/matchesmd", matches_md_resource)


if __name__ == "__main__":
    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=False)
