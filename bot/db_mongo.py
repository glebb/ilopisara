import asyncio
import os

import motor.motor_asyncio
import pymongo.errors
from cachetools import TTLCache, cached
from dotenv import load_dotenv

import helpers
from base_logger import logger
from data import api

client = motor.motor_asyncio.AsyncIOMotorClient()
db = client.ilo

load_dotenv("../.env")
DISCORD_CHANNEL = int(os.getenv("DISCORD_CHANNEL"))
CLUB_ID = os.getenv("CLUB_ID")


async def watch(result_handler):
    resume_token = None
    pipeline = [{"$match": {"operationType": "insert"}}]
    try:
        async with db.matches.watch(pipeline) as stream:
            async for insert_change in stream:
                await result_handler((insert_change["fullDocument"]))
                resume_token = stream.resume_token
    except pymongo.errors.PyMongoError:
        if resume_token is None:
            logger.error("Database connection is fucked, cannot watch for updates")
        else:
            async with db.matches.watch(pipeline, resume_after=resume_token) as stream:
                async for insert_change in stream:
                    await result_handler((insert_change["fullDocument"]))


async def update_matches():
    new_matches = []
    for game_type in helpers.GAMETYPE:
        matches = api.get_matches(count=50, game_type=game_type.value)
        for match in matches:
            match["gameType"] = game_type.value
            update_result = await db.matches.update_one(
                {"matchId": match["matchId"]}, {"$setOnInsert": match}, upsert=True
            )
            if update_result.matched_count == 0:
                new_matches.append(match)
    return new_matches


async def find_matches_by_club_id(versusClubId=None, game_type=None):
    matches = (
        db.matches.find({f"clubs.{versusClubId}": {"$exists": True}}).sort(
            "timestamp", 1
        )
        if versusClubId
        else db.matches.find({"gameType": game_type} if game_type else {}).sort(
            "timestamp", 1
        )
    )
    return await matches.to_list(length=10000)


async def find_match_by_id(matchId):
    matches = db.matches.find({"matchId": matchId})
    return await matches.to_list(length=1)


@cached(cache=TTLCache(maxsize=1024, ttl=180))
async def get_known_team_names():
    temp = db.matches.aggregate(
        [
            {"$project": {"arrayofkeyvalue": {"$objectToArray": "$$ROOT.clubs"}}},
            {"$unwind": "$arrayofkeyvalue"},
            {
                "$group": {
                    "_id": None,
                    "allNames": {"$addToSet": "$arrayofkeyvalue.v.details.name"},
                }
            },
        ]
    )

    data = await temp.to_list(length=10000)
    all_names = sorted(data[0]["allNames"], key=str.casefold)
    temp = db.matches.find({ "clubs." + CLUB_ID : { "$exists" : True } })
    data = await temp.to_list(length=1)
    try:
        own_name = data[0]["clubs"][CLUB_ID]["details"]["name"]
        all_names.insert(0, all_names.pop(all_names.index(own_name)))
    except:
        pass
    return all_names


if __name__ == "__main__":
    asyncio.run(update_matches())
