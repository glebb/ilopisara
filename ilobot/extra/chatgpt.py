import datetime
import json
import random

from dacite import from_dict
from openai import AsyncOpenAI, OpenAIError

from ilobot import data_service, helpers, jsonmap
from ilobot.base_logger import logger
from ilobot.config import CLUB_ID, GPT_MODEL, OPEN_API
from ilobot.data import api
from ilobot.extra.format import format_game_data
from ilobot.helpers import is_overtime
from ilobot.models import Match, MatchType

SKIP_KEYS = (
    "matchId",
    "timeAgo",
    "player_names",
    "toa",
    "raw",
    "teamArtAbbr",
    "opponentTeamArtAbbr",
    "dnf",
    "passc",
    "passa",
    "customKit",
    "teamId",
    "opponentTeamId",
    "OnlineGameType",
    "asset",
    "rank",
    "gameType",
    "clubDivision",
    "memberString",
    "posSorted",
    "timestamp",
    "opponent",
    "playerLevel",
    "platform",
    "losses",
)

SKIP_PLAYER_KEYS = (
    "removedReason",
    "result",
    "score",
    "scoreRaw",
    "scoreString",
    "teamSide",
    "platform",
)

KEY_MAPPINGS = {
    "opponentClubId": "Opponent Club ID",
    "name": "Club name",
}


def handle_keys(data, game_type=None):
    """Skip unwanted keys and convert rest to mapped names"""
    if not game_type:
        game_type = int(data["clubs"][CLUB_ID]["cNhlOnlineGameType"])
    converted_data = {}
    for key, value in data.items():
        original_key = key

        for skip_key in SKIP_KEYS:
            if skip_key in key:
                original_key = None
        if not original_key:
            continue

        # skip power play stats for 3vs3
        if key in ("ppo", "ppg", "skppg") and game_type >= 200:
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
            if key == "class":
                value = helpers.LOADOUTS.get(value, value)

        if isinstance(value, dict):
            # Recursively process nested dictionaries
            converted_data[original_key] = handle_keys(value, game_type)
        elif key in KEY_MAPPINGS:
            # If key is in the mappings, replace it with the full name
            converted_data[KEY_MAPPINGS[key]] = value
        elif key in jsonmap.names:
            # If key is in the mappings, replace it with the full name
            converted_data[jsonmap.names[key]] = value
        else:
            converted_data[key] = value
    return converted_data


def chatify_data(game: dict, skip_player_names=False):
    cleaned_data = handle_keys(game)
    for key in cleaned_data["clubs"].keys():  # keep only our team players
        # if key == str(CLUB_ID):
        cleaned_data["clubs"][key]["players"] = cleaned_data["players"][key]
        # else:
        #    cleaned_data["clubs"][key]["players"] = {}
        cleaned_data["clubs"][key]["no_game"] = check_no_game(game)

    clubs = {}
    for club_id, club_data in cleaned_data["clubs"].items():
        # convert club id to club name
        club_name = club_data["details"]["Club name"]
        clubs[club_name] = club_data
        clubs[club_name]["hits"] = game["aggregate"][club_id]["skhits"]
        clubs[club_name]["clubId"] = club_id
        del clubs[club_name]["details"]

        # add player actual names under the club data
        # if not skip_player_names:
        clubs[club_name]["players"] = {
            (
                player_data["playername"]
                if skip_player_names
                else api.get_member(player_data["playername"]).get(
                    "skplayername", player_data["playername"]
                )
                or player_data["playername"]
            ): player_data
            for player_id, player_data in club_data["players"].items()
        }
        for player in clubs[club_name]["players"]:
            clubs[club_name]["players"][player]["playername"] = player

    del cleaned_data["players"]
    cleaned_data["clubs"] = clubs
    match = from_dict(data_class=Match, data=game)
    overtime = is_overtime(match)
    if overtime:
        cleaned_data["overtime"] = True
    else:
        cleaned_data["overtime"] = False

    return cleaned_data


def check_dnf(game: dict):
    for club in game["clubs"]:
        if (
            game["clubs"][club]["winner by DNF"] != "0"
            or game["clubs"][club]["winner by goalie DNF"] != "0"
        ):
            return True
    return False


def check_no_game(game: dict):
    zero = []
    for club in game["clubs"]:
        if str(game["clubs"][club]["shots"]) == "0":
            zero.append(True)
        else:
            zero.append(False)
    if all(zero):
        return True
    return False


def setup_messages(game, history):
    model = data_service.convert_match(game)
    our_team = game["clubs"][CLUB_ID]["details"]["name"]
    cleaned_game = chatify_data(game)
    cleaned_game["previous_games"] = history if history else {}
    formatted_game = format_game_data(cleaned_game)
    now = datetime.date.today().strftime("%d %B")
    messages = [
        {
            "role": "system",
            "content": f"""You are general manager of hockey club {our_team}.
            You are Finnish. 
            You talk casually. 
            You are very mean spirited. 
            You hate losing and poor performance.
            You are extremly sarcastic about positive results.
            When you talk about your team's ({our_team}) players, you give feedback to them directly.
            You are sometimes drunk.
            You are no stranger to profanities when it's called for.
            You speak in Finnish.""",
        },
        {
            "role": "user",
            "content": """Analyze the hockey game that just took place, based on provided 
            data. If the game was won because of DNF, don't analyze players or the game further. Otherwise, assess the performance of your team and your players directly based on the data. 
            Throw in insults for poor performance. Consider highlighting different perspectives and corporating elements of 
            hockey analogies and real-world comparisons from the world of hockey, to keep the analyses engaging and unique each time.
            Give advice on how to do better.""",
        },
    ]
    messages.append(
        {
            "role": "user",
            "content": "\n###\n" + formatted_game + "\n\n",
        }
    )
    if model.clubs[CLUB_ID].get_match_type().value == MatchType.THREE_ON_THREE.value:
        messages.append(
            {
                "role": "user",
                "content": f"Match was played as 3vs3, meaning each team had 3 skaters and a goalie on ice. This game mode doesn't have regular penalties, only penalty shots. ",
            }
        )
    if random.randint(0, 10) == 0:
        messages.append(
            {
                "role": "user",
                "content": f"If current time of {now} happens to happen during some special occasions, such has halloween, thanksgiving, mid summer, or new year's eve as an example, spice things up with related phrases.",
            }
        )
    if check_dnf(cleaned_game):
        messages.append(
            {
                "role": "user",
                "content": "If the data indicates 'winner by opponent DNF'"
                "make a big deal about the losing team chickening out by not "
                "finishing the game properly.",
            }
        )
    messages.append(
        {"role": "user", "content": "Limit the reply to 280 words maximum."}
    )
    return messages


async def write_gpt_summary(game: dict, history=None):
    messages = setup_messages(game, history)
    try:
        client = AsyncOpenAI(
            api_key=OPEN_API,
        )

        chat_completion = await client.chat.completions.create(
            model=GPT_MODEL,
            messages=messages,
            temperature=1.9,
            top_p=0.2,
            frequency_penalty=1.4,
            presence_penalty=1.2,
        )
    except OpenAIError:
        logger.exception("OPENAI error")
        return None
    return chat_completion.choices[0].message.content
