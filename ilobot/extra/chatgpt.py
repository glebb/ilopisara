import json
import random

import openai
from openai.error import ServiceUnavailableError

from ilobot.base_logger import logger
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
    "skfow",
    "skfol",
    
]

skip_just_player_keys = [
    "removedReason",
    "result",
    "score",
    "scoreRaw",
    "scoreString",
    
]

# Fixed mappings for key name conversions
key_mappings = {
    "opponentClubId": "Opponent Club ID",
    "opponentTeamArtAbbr": "Opponent Team abbreviation",
    "teamArtAbbr": "Team abbreviation",
    "name": "Club name",
    "ppo": "Power-play opportunities"
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
        if key.startswith("skfo") and temp["position"] != "center":
            continue
        if key.startswith("gl"):
            if temp["position"] != "goalie":
                continue
        if "position" in temp:
            if key in skip_just_player_keys:
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
        if key == str(CLUB_ID):
            converted_data["clubs"][key]["players"] = converted_data["players"][key]
        else:
            converted_data["clubs"][key]["players"] = {} 
    
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

def check_dnf(game: dict):
    for club in game["clubs"]:
        if game["clubs"][club]["winnerByDnf"] != "0" or game["clubs"][club]["winnerByGoalieDnf"] != "0":
            return True
    return False

hockey_journalists = ["Bob McKenzie", "Elliotte Friedman", "Pierre LeBrun", "Darren Dreger", "Katie Strang"]

async def write_gpt_summary(game: dict, history=None):
    our_team = game["clubs"][CLUB_ID]["details"]["name"]
    cleaned_game = clean_up_data(game)
    json_output = json.dumps(cleaned_game)
    messages = [
        {
            "role": "system",
            "content": f"You are a crtical hockey journalist. Mimic the style of the writer {random.choice(hockey_journalists)}. You are writing for the fans of club {our_team}. You critique the performance of the players and give praise to those who deserve it, and point out the mistakes of those who don't."
            
        },
        {
            "role": "user",
            "content": "Describe events of a hockey game, that likely took place, based on following json data. Take heavy use of provided analysis and direct quotes from imaginary general manager 'Yoosef', who saw the game and is extremely critical of the perofrmance of the players. He always concentrates on several weaker aspects of individual players."
        }
    ]
    #if random.choice([True, False]):
    #    messages.append({"role": "user", "content": "Have Yoosef additionally comment shots on net, using a phrase 'VETOJA HYVÄT HERRAT!'"})
    #    messages.append({"role": "assistant", "content": "VETOJA HYVÄT HERRAT! We can only win if we shoot!"})
         
    messages.append({"role": "user", "content": json_output})
        
    if check_dnf(cleaned_game):
        messages.append({"role": "user", "content": "If the data indicates 'winnerByDnf' or 'winnerByGoalieDnf' with other than value 0, make a big deal about opponent chickening out by not finishing the game properly. Don't mention the data keys or values as such."})
        messages.append({"role": "assistant", "content": "The opponent cowardly quit the game before it was finished."})
        messages.append({"role": "assistant", "content": "The opponent demonstrated despicable attitude by quitting the match until it was finished."})
    messages.append({"role": "user", "content": "Limit the text to 290 words."})
    
    try:
        chat_completion = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo", messages=messages, temperature=0.9
    )
    except ServiceUnavailableError:
        logger.exception("OPENAI error")
        return None        
    return chat_completion["choices"][0]["message"]["content"]
