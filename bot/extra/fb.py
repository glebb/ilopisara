import firebase_admin
import os
from firebase_admin import credentials
from firebase_admin import firestore
from dotenv import load_dotenv
load_dotenv('../.env')
CLUB_ID = os.getenv('CLUB_ID')


# Use a service account
try:
    cred = credentials.Certificate('../firebase-credentials.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
except:
    print('Firebase not enabled')



def save_match(match, game_type):
    db.collection(game_type).document(match['matchId']).set(match)

def find_matches_by_club_id(versusClubId=None):
    matches = []
    docs = db.collection('matches').stream()
    for doc in docs:
        match = doc.to_dict()
        matchVersusClubid = [x for x in match['clubs'] if x != CLUB_ID][0]
        if matchVersusClubid == versusClubId or versusClubId == None:
            matches.append(match)
    docs2 = db.collection('playoffs').stream()
    for doc in docs2:
        match = doc.to_dict()
        matchVersusClubid = [x for x in match['clubs'] if x != CLUB_ID][0]
        if matchVersusClubid == versusClubId or versusClubId == None:
            matches.append(match)
    return sorted(matches, key=lambda match: float(match['timestamp']))

def find_match_by_id(matchId):
    matches = []
    docs = db.collection('matches').where('matchId', '==', matchId).stream()
    for doc in docs:
        match = doc.to_dict()
        matches.append(match)
    docs2 = db.collection('playoffs').where('matchId', '==', matchId).stream()
    for doc in docs2:
        match = doc.to_dict()
        matches.append(match)
    return matches