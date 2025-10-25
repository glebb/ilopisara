import asyncio

import aiohttp

from ilobot.base_logger import logger
from ilobot.streamer_base import Streamer, StreamStatus
from ilobot.twitch_auth import TwitchAuth


class Twitcher(Streamer):
    def __init__(self, streamer_login: str, auth_instance: TwitchAuth) -> None:
        super().__init__(streamer_identifier=streamer_login, platform_name="Twitch")
        self.auth = auth_instance
        self.params = [("user_login", self.streamer_identifier)]

    def _is_relevant_stream(self, stream_data: dict) -> bool:
        return True
        # if stream_data and isinstance(stream_data.get("game_name"), str):
        #    return stream_data["game_name"].lower().startswith("nhl")
        # return False

    async def update(self) -> StreamStatus:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.twitch.tv/helix/streams",
                    headers=self.auth.get_headers(),
                    params=self.params,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status != 200:
                        logger.error(
                            f"Error - Twitch request for {self.streamer_identifier} returned {response.status}"
                        )
                        content = await response.text()
                        logger.error(content)
                        self.status = StreamStatus.ERROR
                        self.last_exception = Exception(
                            f"Twitch API error {response.status}: {content}"
                        )
                        return self.status

                    sdata = await response.json()
                    logger.info(
                        f"Twitch checked for {self.streamer_identifier}: {sdata.get('data')}"
                    )

            if sdata.get("data") and len(sdata["data"]) > 0:
                stream_info = sdata["data"][0]
                if self._is_relevant_stream(stream_info):
                    logger.info(
                        f"Twitch NHL stream found for {self.streamer_identifier}"
                    )
                    self.stream_url = (
                        "https://www.twitch.tv/" + stream_info["user_login"]
                    )
                    self.stream_title = stream_info.get("title")
                    twitch_started_at = stream_info["started_at"]

                    if self.stream_started_at != twitch_started_at:
                        self.stream_started_at = twitch_started_at
                        self.status = StreamStatus.STARTED
                    else:
                        self.status = StreamStatus.ONGOING
                else:
                    if self.is_live():
                        self.status = StreamStatus.STOPPED
                    else:
                        self.status = StreamStatus.OFFLINE
                    logger.info(
                        f"Twitch stream found for {self.streamer_identifier}, but not NHL game: {stream_info.get('game_name')}"
                    )
            else:
                if self.is_live():
                    self.status = StreamStatus.STOPPED
                else:
                    self.status = StreamStatus.OFFLINE

        except aiohttp.ClientError as e:
            logger.error(
                f"AIOHTTP Error updating Twitch status for {self.streamer_identifier}: {e}"
            )
            self.status = StreamStatus.ERROR
            self.last_exception = e
        except Exception as e:
            logger.error(
                f"Unexpected error updating Twitch status for {self.streamer_identifier}: {e}"
            )
            self.status = StreamStatus.ERROR
            self.last_exception = e

        logger.info(
            f"Twitch status for {self.streamer_identifier}: {self.status.value}"
        )
        return self.status


if __name__ == "__main__":

    async def main_test():
        from ilobot.config import STREAMERS, TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET

        if not TWITCH_CLIENT_ID or not TWITCH_CLIENT_SECRET:
            print("Twitch client ID/secret not configured in .env")
            return

        streamer_logins = STREAMERS.split(",")
        if not streamer_logins or not streamer_logins[0]:
            print("No Twitch streamers configured in .env (TWITCH_STREAMERS)")
            return

        test_streamer_login = streamer_logins[0]
        auth = TwitchAuth()
        twitcher = Twitcher(streamer_login=test_streamer_login, auth_instance=auth)
        status = await twitcher.update()
        print(f"Streamer: {twitcher.streamer_identifier}")
        print(f"Status: {status.value}")
        if twitcher.is_live():
            print(f"Title: {twitcher.stream_title}")
            print(f"URL: {twitcher.stream_url}")
            print(f"Started at: {twitcher.stream_started_at}")
        if twitcher.status == StreamStatus.ERROR and twitcher.last_exception:
            print(f"Error: {twitcher.last_exception}")

    asyncio.run(main_test())
