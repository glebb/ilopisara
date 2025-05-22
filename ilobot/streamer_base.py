from enum import Enum
from abc import ABC, abstractmethod
import datetime

class StreamStatus(Enum):
    STARTED = "started"
    ONGOING = "ongoing"
    STOPPED = "stopped"
    OFFLINE = "offline" # Added for clarity, similar to STOPPED but more explicit for initial state
    ERROR = "error"

class Streamer(ABC):
    def __init__(self, streamer_identifier: str, platform_name: str):
        self.streamer_identifier = streamer_identifier # User-facing name/ID
        self.platform_name = platform_name
        self.status: StreamStatus = StreamStatus.OFFLINE
        self.stream_title: str | None = None
        self.stream_url: str | None = None
        self.stream_started_at: datetime.datetime | str | None = None # str for Twitch, datetime for potential future use
        self.last_exception: Exception | None = None # To store any error during update

    @abstractmethod
    async def update(self) -> StreamStatus:
        """
        Updates the stream status.
        Returns the current StreamStatus.
        Should set self.status, self.stream_title, self.stream_url, self.stream_started_at accordingly.
        """
        pass

    def get_notification_message(self) -> str | None:
        """
        Generates a notification message based on the current status.
        """
        if self.status == StreamStatus.STARTED:
            title = f" - \"{self.stream_title}\"" if self.stream_title else ""
            url = f"\n{self.stream_url}" if self.stream_url else ""
            return f"{self.streamer_identifier} on {self.platform_name} has **started** streaming!{title}{url}"
        elif self.status == StreamStatus.STOPPED:
            # Optionally, you might not want notifications for every stop,
            # or you might want a different message.
            # For now, let's assume we notify on stop as well.
            return f"{self.streamer_identifier} on {self.platform_name} has **stopped** streaming."
        # No message for ONGOING or OFFLINE by default, unless desired.
        return None

    def is_live(self) -> bool:
        return self.status == StreamStatus.STARTED or self.status == StreamStatus.ONGOING
