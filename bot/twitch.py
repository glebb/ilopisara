from enum import Enum

import requests
from base_logger import logger
from helpers import CLIENT_ID, OAUTH, STREAMERS


class TwitchStatus(Enum):
    STARTED = 0
    ONGOING = 1
    STOPPED = 2


class Twitcher:
    def __init__(self) -> None:
        self.status = TwitchStatus.STOPPED
        self.stream_started = ""
        self.stream_url = None
        self.headers = {
            "Client-Id": CLIENT_ID,
            "Authorization": "Bearer " + OAUTH,
        }
        self.params = []
        for streamer in STREAMERS.split(","):
            param = ("user_login", streamer)
            self.params.append(param)

    def _nhl_stream_found(self, data):
        return (
            "data" in data
            and len(data["data"]) > 0
            and data["data"][0]["game_name"].lower().startswith("nhl")
        )

    def update(self):
        try:
            response = requests.get(
                "https://api.twitch.tv/helix/streams",
                headers=self.headers,
                params=self.params,
            )
            data = response.json()
            logger.info(f"Twitch checked {self.params}")
        except (KeyError, ValueError):
            logger.error(
                "Error - make sure your twitch request headers and params are correct."
            )
            self.status = TwitchStatus.STOPPED
            return self.status
        if self._nhl_stream_found(data):
            logger.info(f"Twitch NHL stream found")
            self.stream_url = "https://www.twitch.tv/" + data["data"][0]["user_login"]
            if self.stream_started != data["data"][0]["started_at"]:
                self.stream_started = data["data"][0]["started_at"]
                self.status = TwitchStatus.STARTED
            else:
                self.status = TwitchStatus.ONGOING
        else:
            self.status = TwitchStatus.STOPPED
        logger.info(f"Twitch status: {self.status}")
        return self.status


if __name__ == "__main__":
    twitcher = Twitcher()
    data = twitcher.update()
    if data == TwitchStatus.STARTED:
        print(twitcher.stream_url)
        print(twitcher.stream_started)
