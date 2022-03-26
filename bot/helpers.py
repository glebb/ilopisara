import os
from dotenv import load_dotenv


load_dotenv('../.env')
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL = os.getenv('DISCORD_CHANNEL')

CLUB_ID = os.getenv('CLUB_ID')


def chunk_using_generators(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def is_win(match):
    scores = match['clubs'][os.getenv('CLUB_ID')]['scoreString'].split(' - ')
    return int(scores[0]) > int(scores[1])

def get_match_mark(match):
    if is_win(match):
        mark = ":white_check_mark: "
    else:
        mark = ":x: "
    return mark

def teppo_scores(match):
    for _, p in match['players'][os.getenv('CLUB_ID')].items():
        if p['playername'] == 'bodhi-FIN' and int(p['skgoals']) > 0:
            return True
    return False
