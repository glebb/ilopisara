from pymongo import MongoClient
from dotenv import load_dotenv
from data import api

client = MongoClient()
db = client.ilo

if __name__ == "__main__":
    for type in api.GAMETYPE:
        matches = api.get_matches(count=50, game_type=type.value)
        path = "unknown"
        if type == api.GAMETYPE.REGULARSEASON:
            path = "matches"
        elif type == api.GAMETYPE.PLAYOFFS:
            path = "playoffs"
        for match in matches:
            update_result = db[path].update_one(
                {"matchId": match["matchId"]}, {"$setOnInsert": match}, upsert=True
            )
            if update_result.matched_count == 0:
                print(f"inserted{match}")
