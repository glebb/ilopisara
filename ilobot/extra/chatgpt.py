import json

import openai
from openai.error import RateLimitError, ServiceUnavailableError

from ilobot import jsonmap
from ilobot.base_logger import logger
from ilobot.data import api
from ilobot.helpers import CLUB_ID, GPT_MODEL, OPEN_API

openai.api_key = OPEN_API

SKIP_KEYS = (
    "matchId",
    "timeAgo",
    "aggregate",
    "player_names",
    "toi",
    "toa",
    "raw",
    "teamArtAbbr",
    "opponentTeamArtAbbr",
    "toiseconds",
    "dnf",
    "passc",
    "passa",
    "customKit",
    "teamId",
    "opponentTeamId",
    "OnlineGameType",
    "asset",
    "rank",
    "class",
    "gameType",
    "clubDivision",
    "memberString",
    "posSorted",
    "timestamp",
    "opponent",
    "playerLevel",
    "skfow",
    "skfol",
    "skshotpct",
)

SKIP_PLAYER_KEYS = (
    "removedReason",
    "result",
    "score",
    "scoreRaw",
    "scoreString",
    "teamSide",
)

KEY_MAPPINGS = {
    "opponentClubId": "Opponent Club ID",
    "name": "Club name",
}


def handle_keys(data):
    """Skip unwanted keys and convert rest to mapped names"""
    converted_data = {}
    for key, value in data.items():
        original_key = key

        for skip_key in SKIP_KEYS:
            if skip_key in key:
                original_key = None
        if not original_key:
            continue
        if key.startswith("sk"):  # skip skater stats if goalie
            if data["position"] == "goalie":
                continue
        if (
            key.startswith("skfo") and data["position"] != "center"
        ):  # skip faceoff stats if not center
            continue
        if key.startswith("gl"):  # skip goalie stats if not goalie
            if data["position"] != "goalie":
                continue

        if "position" in data:  # player data
            if key in SKIP_PLAYER_KEYS:
                continue
            if key == "skgiveaways" and int(data["skgiveaways"]) < 5:
                continue

        if isinstance(value, dict):
            # Recursively process nested dictionaries
            converted_data[original_key] = handle_keys(value)
        elif key in KEY_MAPPINGS:
            # If key is in the mappings, replace it with the full name
            converted_data[KEY_MAPPINGS[key]] = value
        elif key in jsonmap.names:
            # If key is in the mappings, replace it with the full name
            converted_data[jsonmap.names[key]] = value
        else:
            converted_data[key] = value
    return converted_data


def chatify_data(game: dict):
    cleaned_data = handle_keys(game)
    for key in cleaned_data["clubs"].keys():  # keep only our team players
        if key == str(CLUB_ID):
            cleaned_data["clubs"][key]["players"] = cleaned_data["players"][key]
        else:
            cleaned_data["clubs"][key]["players"] = {}

    clubs = {}
    for club_id, club_data in cleaned_data["clubs"].items():
        # convert club id to club name
        club_name = club_data["details"]["Club name"]
        clubs[club_name] = club_data
        clubs[club_name]["clubId"] = club_id
        del clubs[club_name]["details"]

        # add player actual names under the club data
        clubs[club_name]["players"] = {
            api.get_member(player_data["playername"])["skplayername"]
            or player_data["playername"]: player_data
            for player_id, player_data in club_data["players"].items()
        }
        for player in clubs[club_name]["players"]:
            clubs[club_name]["players"][player]["playername"] = player

    del cleaned_data["players"]
    cleaned_data["clubs"] = clubs
    return cleaned_data


def check_dnf(game: dict):
    for club in game["clubs"]:
        if (
            game["clubs"][club]["winner by DNF"] != "0"
            or game["clubs"][club]["winner by goalie DNF"] != "0"
        ):
            return True
    return False


def setup_messages(game, history):
    our_team = game["clubs"][CLUB_ID]["details"]["name"]
    cleaned_game = chatify_data(game)
    game_json_output = json.dumps(cleaned_game)
    history_json_output = json.dumps({"previous_games": history})
    messages = [
        {
            "role": "system",
            "content": f"You are a Yoosef, entitled general manager of hockey club {our_team}."
            "You are mean, point out the mistakes players make and give praise only on "
            "most exceptional performances.",
        },
        {
            "role": "user",
            "content": "Analyze the hockey game that just took place, based on following "
            "json data and imaginary events. Critique the performance of your team and your "
            "players. Throw insults if needed to make a point. ",
        },
    ]
    if (
        game["clubs"][CLUB_ID]["losses"] != "0"
        and int(game["clubs"][CLUB_ID]["shots"]) < 20
    ):
        messages.append(
            {
                "role": "user",
                "content": "Comment the poor shots statistics with a phrase 'VETOJA HYVÄT HERRAT!'",
            }
        )

    messages.append({"role": "user", "content": "\n###\n" + game_json_output + "\n"})
    messages.append({"role": "user", "content": "\n###\n" + history_json_output + "\n"})

    if check_dnf(cleaned_game):
        messages.append(
            {
                "role": "user",
                "content": "If the data indicates 'winner by DNF' or 'winner by goalie DNF' "
                "with other than value 0, make a big deal about the other team chickening out by not "
                "finishing the game properly. Don't mention the data keys or values as such. "
                f"If it was the opponent who won by {our_team} not finishing the team, raise hell.",
            }
        )
        messages.append(
            {
                "role": "assistant",
                "content": "The team cowardly quit the game before it was finished.",
            }
        )
    messages.append(
        {"role": "user", "content": "Limit the reply to 290 words maximum."}
    )
    return messages


async def write_gpt_summary(game: dict, history=None):
    messages = setup_messages(game, history)
    try:
        chat_completion = await openai.ChatCompletion.acreate(
            model=GPT_MODEL,
            messages=messages,
            temperature=1.33,
            top_p=0.5,
            frequency_penalty=0.3,
            presence_penalty=1,
        )
    except (ServiceUnavailableError, RateLimitError):
        logger.exception("OPENAI error")
        return None

    return chat_completion["choices"][0]["message"]["content"]
