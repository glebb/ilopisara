import os

from dotenv import load_dotenv
from data import api
from extra import features, fb, giphy, twitch
import helpers
import data_service

load_dotenv("../.env")
CHANNEL = int(os.getenv("DISCORD_CHANNEL"))
MATCH_CHANNEL = int(os.getenv("DISCORD_CHANNEL"))


match_results_storage = {}


async def get_latest_results(bot):
    if len(match_results_storage) == 0:
        initial = True
    else:
        initial = False
    regularmatches = api.get_matches()
    playoffs = api.get_matches(game_type=api.GAMETYPE.PLAYOFFS.value)
    matches = regularmatches + playoffs
    matches = sorted(matches, key=lambda match: float(match["timestamp"]))
    for i in reversed(range(0, len(matches))):
        match_id = matches[i]["matchId"]
        if not match_id in match_results_storage:
            match_results_storage[match_id] = matches[i]
            if features.firebase_enabled():
                if matches[i] in regularmatches:
                    game_type = "matches"
                else:
                    game_type = "playoffs"
                fb.save_match(matches[i], game_type)
            if not initial:
                if helpers.is_win(matches[i]):
                    mark = ":white_check_mark: "
                    gif = giphy.get_win()
                else:
                    mark = ":x: "
                    gif = giphy.get_fail()
                await bot._http.send_message(
                    MATCH_CHANNEL, mark + data_service.format_result(matches[i])
                )
                await bot._http.send_message(MATCH_CHANNEL, gif)
                await bot._http.send_message(
                    MATCH_CHANNEL, data_service.match_details(matches[i])
                )


async def twitch_poller(bot):
    stream = twitch.get_live_stream()
    if stream and stream['status'] == 'start':
        await bot._http.send_message(CHANNEL, "Stream started: " +stream['url'])
