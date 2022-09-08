from data import api
from pymongo import MongoClient

client = MongoClient()
db = client.ilo


def update_matches():
    new_matches = []
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
                new_matches.append(match)
    return new_matches


def find_matches_by_club_id(versusClubId=None):
    matches = (
        db.matches.find({f"clubs.{versusClubId}": {"$exists": True}})
        if versusClubId
        else db.matches.find()
    )
    playoff_matches = (
        db.playoffs.find({f"clubs.{versusClubId}": {"$exists": True}})
        if versusClubId
        else db.playoffs.find()
    )
    return sorted(
        list(matches) + list(playoff_matches),
        key=lambda match: float(match["timestamp"]),
    )


def find_match_by_id(matchId):
    matches = db.matches.find({"matchId": matchId})
    playoff_matches = db.playoffs.find({"matchId": matchId})
    return list(matches) + list(playoff_matches)


if __name__ == "__main__":
    print(len(find_matches_by_club_id(121775)))
