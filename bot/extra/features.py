from cachetools import cached
from dotenv import load_dotenv
from firebase_admin import credentials

load_dotenv('../../.env')

@cached(cache={})
def firebase_enabled():
    try:
        credentials.Certificate('../firebase-credentials.json')
    except (IOError, ValueError, FileNotFoundError):
        print('Firebase not enabled. To enable, create ../firebase-credentials.json')
        return False
    return True

@cached(cache={})
def giphy_enabled():
    return True

@cached(cache={})
def twitch_enabled():
    return True

@cached(cache={})
def youtube_enabled():
    return False