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
    matches = api.get_matches(count=50)
    batch = db.batch()
    for match in matches:
        print(match['matchId'])
        doc_ref = db.collection('matches').document(match['matchId'])
        batch.set(doc_ref, match)
    batch.commit()

