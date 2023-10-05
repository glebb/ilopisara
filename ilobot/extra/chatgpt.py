import json
import random

import openai

from ilobot.helpers import CLUB_ID, OPEN_API
from ilobot.jsonmap import match

openai.api_key = OPEN_API

skip_keys = [
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
    
]

# Fixed mappings for key name conversions
key_mappings = {
    "opponentClubId": "Opponent Club ID",
    "opponentTeamArtAbbr": "Opponent Team abbreviation",
    "teamArtAbbr": "Team abbreviation",
    "name": "Club name",
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
        if key.startswith("gl"):
            if temp["position"] != "goalie":
                continue

        if isinstance(value, dict):
            # Recursively process nested dictionaries
            converted_data[xxx] = convert_keys(value)
        elif key in key_mappings:
            # If key is in the mappings, replace it with the full name
            converted_data[key_mappings[key]] = value
        elif key in match:
            # If key is in the mappings, replace it with the full name
            converted_data[match[key]] = value
        else:
            converted_data[key] = value
    return converted_data

def clean_up_data(game: dict):
    converted_data = convert_keys(game)
    for key in converted_data["clubs"].keys():
        converted_data["clubs"][key]["players"] = converted_data["players"][key]
    
    clubs = {}    
    for club_id, club_data in converted_data["clubs"].items():
        club_name = club_data["details"]["Club name"]
        clubs[club_name] = club_data
        clubs[club_name]["clubId"] = club_id
        del clubs[club_name]["details"]
        clubs[club_name]["players"] = {
            player_data["playername"]: player_data
            for player_id, player_data in club_data["players"].items()
        
    }
    del converted_data["players"]
    converted_data['clubs'] = clubs                     
    return converted_data

hockey_journalists = ["Bob McKenzie", "Elliotte Friedman", "Pierre LeBrun", "Darren Dreger", "Katie Strang"]

async def write_gpt_summary(game: dict):
    our_team = game["clubs"][CLUB_ID]["details"]["name"]
    json_output = json.dumps(clean_up_data(game))
    messages = [
        {
            "role": "system",
            "content": f"You are a hockey journalist. Mimic the style of the writer {random.choice(hockey_journalists)}. You are writing for the fans of club {our_team}"
            
        },
        {
            "role": "user",
            "content": "Describe events of a hockey game, that likely took place, based on following json data."
        }
    ]

    messages.append({"role": "user", "content": json_output})
    
    
    messages.append({"role": "user", "content": "Critique the performance of the players. Give praise to those who deserve it, and point out the mistakes of those who don't."})
    if random.choice([True, False]):
        messages.append({"role": "user", "content": f"Include a comment from a fan of club {our_team}, with a made up name."})
    messages.append({"role": "user", "content": "Limit the text to 290 words."})
    
    chat_completion = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo", messages=messages, temperature=0.85
    )
    return chat_completion["choices"][0]["message"]["content"]
