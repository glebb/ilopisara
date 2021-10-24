import jsonmap
from datetime import datetime
import pytz

to_zone = pytz.timezone('Europe/Helsinki')

def find(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return None

def format_result(match):
    ts = int(match['timestamp'])
    score_time = datetime.fromtimestamp(ts)
    score_time = score_time.astimezone(to_zone).strftime('%d.%m. %H:%M')
    opponentId = match['clubs']['19963']['opponentClubId']
    score_teams = match['clubs']['19963']['details']['name'] + ' - ' + match['clubs'][opponentId]['details']['name']
    score_result = match['clubs']['19963']['scoreString']
    score_string = score_time + ' ' + score_teams + ' ' + score_result + ' '
    return score_string

def format_stats(data, stats_filter):
    message = ""
    for k, v in sorted(data.items()):
        stat = None
        key = jsonmap.get_name(k)
        if stats_filter and key.startswith(stats_filter.lower()):
            stat = key + ': ' + v
        elif not stats_filter:
            if not key.startswith('skater') and not key.startswith('goalie') and not key.startswith('xfactor'):
                stat = key + ': ' + v
        if stat:
            message += stat + "\n"
    if message:
        return message
