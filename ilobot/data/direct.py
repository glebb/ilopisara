import urllib.parse

import requests
from requests.adapters import HTTPAdapter
from simplejson import JSONDecodeError
from urllib3.util import Retry

from ilobot.base_logger import logger
from ilobot.config import EA_API_BASE_URL

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Accept headers
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    # Origin and Referer (critical for bot protection bypass!)
    "Referer": "https://www.ea.com/games/nhl/nhl-26",
    "Origin": "https://www.ea.com",
    # Chrome security headers (sec-ch-ua)
    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    # Fetch metadata headers
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    # Additional headers
    "DNT": "1",
    "Connection": "keep-alive",
}


retry_strategy = Retry(total=2, backoff_factor=0.2)

adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)


def get_members(club_id, platform):
    data = {}
    try:
        url = f"{EA_API_BASE_URL}members/career/stats?platform={platform}&clubId={club_id}"
        logger.info(f"Fetching url: {url}")
        data = http.get(url, timeout=10, headers=headers).json()
    except (requests.exceptions.Timeout, JSONDecodeError) as err:
        logger.error(err)
    return data


def get_matches(club_id, platform, count, game_type):
    data = []
    try:
        url = (
            f"{EA_API_BASE_URL}clubs/matches?matchType="
            f"{str(game_type)}&platform={platform}&clubIds={club_id}&maxResultCount={count}"
        )
        logger.info(f"Fetching url: {url}")
        data = http.get(url, timeout=10, headers=headers).json()
    except (requests.exceptions.Timeout, JSONDecodeError) as err:
        logger.error(err)
    return data


def get_team_record(team, platform):
    data = {}
    try:
        team_quoted = urllib.parse.quote(team)
        url = (
            f"{EA_API_BASE_URL}clubs/search?platform={platform}&clubName={team_quoted}"
        )
        logger.info(f"Fetching url: {url}")
        data = http.get(url, timeout=10, headers=headers).json()
    except (requests.exceptions.Timeout, JSONDecodeError) as err:
        logger.error(err)
    return data


def get_team_info(team_id, platform):
    data = {}
    try:
        url = f"{EA_API_BASE_URL}clubs/info?platform={platform}&clubIds={team_id}"
        logger.info(f"Fetching url: {url}")
        data = http.get(url, timeout=4, headers=headers).json()
    except (requests.exceptions.Timeout, JSONDecodeError) as err:
        logger.error(err)
    return data


def get_seasonal_stats(team_id, platform):
    data = {}
    try:
        url = f"{EA_API_BASE_URL}clubs/seasonalStats?platform={platform}&clubIds={team_id}"
        logger.info(f"Fetching url: {url}")
        data = http.get(url, timeout=10, headers=headers).json()
    except (requests.exceptions.Timeout, JSONDecodeError) as err:
        logger.error(err)
    return data


def get_member(member_name, platform):
    data = {}
    try:
        url = f"{EA_API_BASE_URL}members/search?platform={platform}&memberName={member_name}"
        logger.info(f"Fetching url: {url}")
        data = http.get(url, timeout=10, headers=headers).json()
    except (requests.exceptions.Timeout, JSONDecodeError) as err:
        logger.error(err)
    return data


def get_rankings(platform, type):
    data = {}
    try:
        url = f"{EA_API_BASE_URL}{type}RankLeaderboard?platform={platform}"
        logger.info(f"Fetching url: {url}")
        data = http.get(url, timeout=10, headers=headers).json()
    except (requests.exceptions.Timeout, JSONDecodeError) as err:
        logger.error(err)
    return data
