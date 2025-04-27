from datetime import datetime, timedelta

import requests

from ilobot.base_logger import logger
from ilobot.config import TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET


class TwitchAuth:
    def __init__(self):
        self.client_id = TWITCH_CLIENT_ID
        self.client_secret = TWITCH_CLIENT_SECRET
        self.access_token = None
        self.expires_at = None

    def get_valid_token(self):
        """Returns a valid access token, refreshing if necessary."""
        if (
            not self.access_token
            or not self.expires_at
            or datetime.now() >= self.expires_at
        ):
            self._refresh_token()
        return self.access_token

    def _refresh_token(self):
        """Refreshes the access token using client credentials flow."""
        try:
            response = requests.post(
                "https://id.twitch.tv/oauth2/token",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "client_credentials",
                },
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()

            self.access_token = data["access_token"]
            # Set expiry time with a small buffer (5 minutes) before actual expiry
            self.expires_at = datetime.now() + timedelta(
                seconds=data["expires_in"] - 300
            )
            logger.info("Successfully refreshed Twitch access token")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to refresh Twitch token: {str(e)}")
            raise

    def get_headers(self):
        """Returns the authorization headers needed for Twitch API calls."""
        return {
            "Client-Id": self.client_id,
            "Authorization": f"Bearer {self.get_valid_token()}",
        }
