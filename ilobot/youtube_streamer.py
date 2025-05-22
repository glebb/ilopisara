import asyncio
from typing import Optional, Tuple

from googleapiclient.discovery import Resource, build
from googleapiclient.errors import HttpError

from ilobot.base_logger import logger
from ilobot.streamer_base import Streamer, StreamStatus

# Store service instance at class level to avoid re-initializing on every object creation
# if multiple Youtuber objects are used with the same API key.
_youtube_services = {}


def get_youtube_service_instance(api_key: str) -> Optional[Resource]:
    """Initializes and returns a YouTube API service object using an API Key."""
    global _youtube_services
    if api_key in _youtube_services:
        return _youtube_services[api_key]

    if not api_key or api_key == "YOUR_YOUTUBE_API_KEY_HERE":
        logger.error("YOUTUBE_API_KEY is not set or is a placeholder.")
        return None
    try:
        service = build("youtube", "v3", developerKey=api_key)
        _youtube_services[api_key] = service
        logger.info("Successfully initialized YouTube service.")
        return service
    except Exception as e:
        logger.error(f"Error building YouTube service: {e}")
        return None


class Youtuber(Streamer):
    def __init__(self, channel_input: str, api_key: str):
        super().__init__(streamer_identifier=channel_input, platform_name="YouTube")
        self.api_key = api_key
        self.youtube_service: Optional[Resource] = get_youtube_service_instance(api_key)
        self.resolved_channel_id: Optional[str] = None
        # self.status is initialized in Streamer base class to OFFLINE

    async def _resolve_channel_id_async(self) -> Optional[str]:
        if not self.youtube_service:
            return None

        # If it looks like a channel ID, use it directly
        if self.streamer_identifier.startswith(
            "UC"
        ) or self.streamer_identifier.startswith("HC"):
            self.resolved_channel_id = self.streamer_identifier
            return self.resolved_channel_id

        # Otherwise, try to resolve username/custom URL
        logger.info(
            f"Attempting to resolve YouTube input '{self.streamer_identifier}' to a channel ID."
        )
        try:
            # Run synchronous Google API calls in a thread
            request = self.youtube_service.channels().list(
                part="id", forUsername=self.streamer_identifier
            )
            response = await asyncio.to_thread(request.execute)
            if response.get("items"):
                self.resolved_channel_id = response["items"][0]["id"]
                logger.info(
                    f"Resolved '{self.streamer_identifier}' to Channel ID: {self.resolved_channel_id}"
                )
                return self.resolved_channel_id
            else:
                # Try searching by query if forUsername fails
                search_request = self.youtube_service.search().list(
                    part="snippet",
                    q=self.streamer_identifier,
                    type="channel",
                    maxResults=1,
                )
                search_response = await asyncio.to_thread(search_request.execute)
                if search_response.get("items"):
                    self.resolved_channel_id = search_response["items"][0]["snippet"][
                        "channelId"
                    ]
                    logger.info(
                        f"Resolved '{self.streamer_identifier}' via search to Channel ID: {self.resolved_channel_id}"
                    )
                    return self.resolved_channel_id
        except HttpError as e:
            logger.error(
                f"YouTube API HTTP error resolving channel '{self.streamer_identifier}': {e.content}"
            )
            self.last_exception = e
        except Exception as e:
            logger.error(
                f"Error resolving YouTube channel '{self.streamer_identifier}': {e}"
            )
            self.last_exception = e

        logger.warning(
            f"Could not resolve '{self.streamer_identifier}' to a YouTube Channel ID."
        )
        return None

    async def _get_live_stream_details_async(
        self,
    ) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
        """Checks live status and returns (is_live, title, video_id, published_at)."""
        if not self.youtube_service or not self.resolved_channel_id:
            return False, None, None, None
        try:
            request = self.youtube_service.search().list(
                part="snippet",
                channelId=self.resolved_channel_id,
                eventType="live",
                type="video",
            )
            response = await asyncio.to_thread(request.execute)
            if response.get("items"):
                stream_details = response["items"][0]["snippet"]
                video_id = response["items"][0]["id"]["videoId"]
                # publishedAt is a string like '2023-10-26T18:00:00Z'
                return (
                    True,
                    stream_details["title"],
                    video_id,
                    stream_details["publishedAt"],
                )
            else:
                return False, None, None, None
        except HttpError as e:
            logger.error(
                f"YouTube API HTTP error checking live status for {self.resolved_channel_id}: {e.content}"
            )
            self.last_exception = e
        except Exception as e:
            logger.error(
                f"Error checking YouTube live status for {self.resolved_channel_id}: {e}"
            )
            self.last_exception = e
        return False, None, None, None

    async def update(self) -> StreamStatus:
        if not self.youtube_service:
            logger.warning(
                f"YouTube service not available for {self.streamer_identifier}. Skipping update."
            )
            self.status = StreamStatus.ERROR  # Or a more specific status
            self.last_exception = Exception("YouTube service not initialized")
            return self.status

        if not self.resolved_channel_id:
            await self._resolve_channel_id_async()
            if not self.resolved_channel_id:
                logger.warning(
                    f"Could not resolve channel ID for {self.streamer_identifier}. Update failed."
                )
                self.status = StreamStatus.ERROR
                self.last_exception = self.last_exception or Exception(
                    "Channel ID resolution failed"
                )
                return self.status

        self.last_exception = None  # Clear previous exception before new attempt
        is_live, title, video_id, published_at_str = (
            await self._get_live_stream_details_async()
        )

        if is_live and video_id:
            self.stream_title = title
            self.stream_url = f"https://www.youtube.com/watch?v={video_id}"
            # Convert publishedAt string to datetime object if needed, or store as string
            # For consistency with Streamer.stream_started_at, we can store as string or parse
            # Let's store as string for now, as Twitch also provides a string.
            # If precise datetime objects are needed later, parsing can be added.

            if self.stream_started_at != published_at_str:
                self.stream_started_at = published_at_str
                self.status = StreamStatus.STARTED
            else:
                self.status = StreamStatus.ONGOING
            logger.info(
                f"YouTube stream for {self.streamer_identifier} ({self.resolved_channel_id}) is LIVE: {title}"
            )
        else:
            if self.is_live():  # Was previously live
                self.status = StreamStatus.STOPPED
                logger.info(
                    f"YouTube stream for {self.streamer_identifier} ({self.resolved_channel_id}) has stopped."
                )
            else:
                self.status = StreamStatus.OFFLINE
                logger.debug(
                    f"YouTube stream for {self.streamer_identifier} ({self.resolved_channel_id}) is offline."
                )
            # Clear stream-specific info if not live
            self.stream_title = None
            self.stream_url = None
            # self.stream_started_at = None # Keep last started_at for comparison if it just stopped

        if self.last_exception:  # If an error occurred during API calls
            self.status = StreamStatus.ERROR

        logger.info(
            f"YouTube status for {self.streamer_identifier} ({self.resolved_channel_id}): {self.status.value}"
        )
        return self.status


if __name__ == "__main__":
    # Example Usage (requires YOUTUBE_API_KEY and YOUTUBE_STREAMERS in .env)
    async def main_test_youtube():
        from ilobot.config import YOUTUBE_API_KEY, YOUTUBE_STREAMERS

        if not YOUTUBE_API_KEY or YOUTUBE_API_KEY == "YOUR_YOUTUBE_API_KEY_HERE":
            print("YOUTUBE_API_KEY not configured in .env or is placeholder.")
            return

        streamer_inputs = YOUTUBE_STREAMERS.split(",")
        if not streamer_inputs or not streamer_inputs[0]:
            print("No YouTube streamers configured in .env (YOUTUBE_STREAMERS)")
            return

        test_streamer_input = streamer_inputs[
            0
        ]  # Test with the first configured streamer

        youtuber = Youtuber(channel_input=test_streamer_input, api_key=YOUTUBE_API_KEY)
        status = await youtuber.update()

        print(
            f"Streamer: {youtuber.streamer_identifier} (Resolved ID: {youtuber.resolved_channel_id})"
        )
        print(f"Status: {status.value}")
        if youtuber.is_live():
            print(f"Title: {youtuber.stream_title}")
            print(f"URL: {youtuber.stream_url}")
            print(f"Started at: {youtuber.stream_started_at}")
        if youtuber.status == StreamStatus.ERROR and youtuber.last_exception:
            print(f"Error: {youtuber.last_exception}")

    asyncio.run(main_test_youtube())
