import json
import os

import falcon
import falcon.asgi
import uvicorn
from dotenv import load_dotenv

from ilobot import calculations, db_mongo

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
    middleware=[AuthMiddleware()],
)

matches_resource = MatchesResource()
app.add_route("/matches", matches_resource)

winpct_resource = WinsResources()
app.add_route("/winpct", winpct_resource)


if __name__ == "__main__":
    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=False)
