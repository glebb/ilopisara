import json

import openai

from ilobot.helpers import OPEN_API

openai.api_key = OPEN_API

skip_keys = [
    "matchId",
    "timeAgo",
    "aggregate",
    "player_names",
    "toi",
    "toa",
    "Raw",
    "teamArtAbbr",
    "opponentTeamArtAbbr",
    "toiseconds",
    "rating",
    "dnf",
    "passc",
    "passa",
]

# Fixed mappings for key name conversions
key_mappings = {
    "opponentClubId": "Opponent Club ID",
    "opponentTeamId": "Opponent Team ID",
}


# Function to convert key names using fixed mappings
def convert_keys(temp):
    converted_data = {}
    for key, value in temp.items():
        xxx = key
        for skip_key in skip_keys:
            if skip_key in key:
                xxx = None
        if not xxx:
            continue
        if key.startswith("sk"):
            if temp["position"] == "goalie":
                continue
            xxx = key.replace("sk", "skater_")
        if key.startswith("gl"):
            if temp["position"] != "goalie":
                continue
            xxx = key.replace("gl", "goalie_")

        if isinstance(value, dict):
            # Recursively process nested dictionaries
            converted_data[xxx] = convert_keys(value)
        elif key in key_mappings:
            # If key is in the mappings, replace it with the full name
            converted_data[key_mappings[key]] = value
        else:
            converted_data[xxx] = value
    return converted_data


def write_gpt_summary(game: dict):
    converted_data = convert_keys(game)
    for key in converted_data["clubs"].keys():
        converted_data["clubs"][key]["players"] = converted_data["players"][key]
    del converted_data["players"]

    # Convert the converted data to JSON
    json_output = json.dumps(converted_data)
    messages = [
        {
            "role": "user",
            "content": "Write a text describing made up events of a hockey game, based on following data. Limit the text to 1900 characters.",
        }
    ]
    messages.append({"role": "user", "content": json_output})
    chat_completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages, temperature=0.8
    )
    return chat_completion["choices"][0]["message"]["content"]
