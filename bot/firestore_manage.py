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
app = firebase_admin.initialize_app(cred)


db = firestore.client()


if __name__ == '__main__':
    m = db.collection(u'matches').stream()
    p = db.collection(u'playoffs').stream()
    matches = []
    for doc in m:
        d = doc.to_dict()
        matches.append(str(d['matchId']))
    playoffs = []
    for doc in p:
        d = doc.to_dict()
        playoffs.append(str(d['matchId']))
    for x in playoffs:
        if x in matches:
            print(x)
