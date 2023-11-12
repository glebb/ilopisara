import urllib.parse

import requests
from requests.adapters import HTTPAdapter
from simplejson import JSONDecodeError
from urllib3.util import Retry

from ilobot.base_logger import logger
from ilobot.config import EA_API_BASE_URL

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:77.0) Gecko/20100101 Firefox/77.0"
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
