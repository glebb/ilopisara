import asyncio

import db_utils
import helpers
import motor.motor_asyncio
import pymongo.errors
from base_logger import logger
from cachetools import TTLCache, cached
from data import api

client = motor.motor_asyncio.AsyncIOMotorClient()
db = client.ilo


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
    for game_type in helpers.GAMETYPE:
        matches = api.get_matches(count=50, game_type=game_type.value)
        for match in matches:
            await db.replica.update_one(
                {"matchId": match["matchId"]}, {"$setOnInsert": match}, upsert=True
            )
            enriched_match = db_utils.enrich_match(match, game_type)
            await db.matches.update_one(
                {"matchId": match["matchId"]},
                {"$setOnInsert": enriched_match},
                upsert=True,
            )
            await db.opponents.update_one(
                {"name": enriched_match["opponent"]["name"]},
                {"$setOnInsert": enriched_match["opponent"]},
                upsert=True,
            )
            # if update_result.matched_count == 0:


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
    temp = db.opponents.find({}, {"name": 1})
    data = await temp.to_list(length=10000)
    return map(lambda x: x["name"], data)


async def find_matches_for_player(player_id):
    matches = db.matches.find(
        {f"players.{helpers.CLUB_ID}.{player_id}": {"$exists": True}}
    ).sort("timestamp", 1)
    return await matches.to_list(length=10000)


if __name__ == "__main__":
    asyncio.run(update_matches())
