import firebase_admin
import os
from firebase_admin import credentials
from firebase_admin import firestore
from dotenv import load_dotenv
from data import api
load_dotenv('../.env')
CLUB_ID = os.getenv('CLUB_ID')


# Use a service account
cred = credentials.Certificate('../firebase-credentials.json')
firebase_admin.initialize_app(cred)

db = firestore.client()


if __name__ == '__main__':
    for type in api.GAMETYPE:
        matches = api.get_matches(count=50, game_type=type.value)
        path = 'unknown'
        if type == api.GAMETYPE.REGULARSEASON:
            path = 'matches'
        elif type == api.GAMETYPE.PLAYOFFS:
            path = 'playoffs'
        batch = db.batch()
        for match in matches:
            print(match['matchId'])
            doc_ref = db.collection(path).document(match['matchId'])
            batch.set(doc_ref, match)
        batch.commit()

