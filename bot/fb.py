import firebase_admin
import os
from firebase_admin import credentials
from firebase_admin import firestore
import data_service
from dotenv import load_dotenv
load_dotenv('../.env')
CLUB_ID = os.getenv('CLUB_ID')


# Use a service account
cred = credentials.Certificate('./firebase-credentials.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

def save_match(match):
    db.collection('matches').document(match['matchId']).set(match)

def find_matches_by_club_id(versusClubId):
    if versusClubId == CLUB_ID:
        return []
    matches = []
    docs = db.collection('matches').stream()
    for doc in docs:
        match = doc.to_dict()
        matchVersusClubid = [x for x in match['clubs'] if x != CLUB_ID][0]
        if matchVersusClubid == versusClubId:
            matches.append(match)
    return matches

def find_match_by_id(matchId):
    matches = []
    docs = db.collection('matches').where('matchId', '==', matchId).stream()
    for doc in docs:
        match = doc.to_dict()
        matches.append(match)
    return matches

if __name__ == '__main__':
    matches = find_matches_by_club_id("12172")
    for match in matches:
        print(data_service.format_result(match))
    match = find_match_by_id("904207420418")
    print(data_service.format_result(match))
