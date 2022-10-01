import requests
from helpers import CLIENT_ID, OAUTH, STREAMERS

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
        and data["data"][0]["game_name"].lower().startswith("nhl")
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
    data = get_live_stream()
    if data and data["data"][0]["game_name"].lower().startswith("nhl"):
        print("https://www.twitch.tv/" + data["data"][0]["user_login"])
