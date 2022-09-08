import json
import os

import requests
from dotenv import load_dotenv

load_dotenv("../.env")
CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
OAUTH = os.getenv("TWITCH_OAUTH")
STREAMERS = os.getenv("TWITCH_STREAMERS")

headers = {
    "Client-Id": CLIENT_ID,
    "Authorization": "Bearer " + OAUTH,
}

live = None

params = []
for streamer in STREAMERS.split(","):
    param = ("user_login", streamer)
    params.append(param)


def get_live_stream():
    global live
    try:
        response = requests.get(
            "https://api.twitch.tv/helix/streams", headers=headers, params=params
        )
        data = response.json()
    except (KeyError, ValueError):
        print("Error - make sure your headers and params are correct.")
        live = None
        return None
    if (
        "data" in data
        and len(data["data"]) > 0
        and data["data"][0]["game_name"].lower() == "nhl 22"
    ):
        url = "https://www.twitch.tv/" + data["data"][0]["user_login"]
        if not live or live != data["data"][0]["started_at"]:
            live = data["data"][0]["started_at"]
            return {"status": "start", "url": url}
        return None
    if live:
        live = None
        return {"status": "stop"}


if __name__ == "__main__":
    f = open(
        "twitch.json",
    )
    data = json.load(f)
    f.close()
    print(data)
    if data["data"][0]["game_name"].lower() == "nhl 22":
        print("https://www.twitch.tv/" + data["data"][0]["user_login"])
