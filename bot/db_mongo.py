import asyncio
import getopt
import sys

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
                logger.info("Db insert")
                await result_handler((insert_change["fullDocument"]))
                resume_token = stream.resume_token
    except pymongo.errors.PyMongoError:
        if resume_token is None:
            logger.error("Database connection is fucked, cannot watch for updates")
        else:
            async with db.matches.watch(pipeline, resume_after=resume_token) as stream:
                async for insert_change in stream:
                    logger.info("Db insert")
                    await result_handler((insert_change["fullDocument"]))


async def update_matches(club_id, platform):
    for game_type in helpers.GAMETYPE:
        postfix = ""
        if club_id != helpers.CLUB_ID:
            postfix = "_" + club_id + "_" + platform
        matches = api.get_matches(
            club_id=club_id, platform=platform, count=10, game_type=game_type.value
        )
        for match in reversed(matches):
            await db["replica" + postfix].update_one(
                {"matchId": match["matchId"]}, {"$setOnInsert": match}, upsert=True
            )
            try:
                enriched_match = db_utils.enrich_match(match, game_type)
            except TypeError:
                logger.error(f"Could not enrich matchId {match['matchId']}")
                continue
            await db["matches" + postfix].update_one(
                {"matchId": match["matchId"]},
                {"$setOnInsert": enriched_match},
                upsert=True,
            )
            await db["opponents" + postfix].update_one(
                {"name": enriched_match["opponent"]["name"]},
                {"$setOnInsert": enriched_match["opponent"]},
                upsert=True,
            )
            # if update_result.matched_count == 0:


async def find_matches_by_club_id(versusClubId=None, game_type=None, player_name=None):
    query = {}
    if game_type:
        query["gameType"] = game_type
    if player_name:
        query["player_names"] = {"$elemMatch": {"name": player_name}}
    if versusClubId:
        query["opponent.id"] = versusClubId
    matches = db.matches.find(query).sort("timestamp", 1)
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
    club_id = helpers.CLUB_ID
    platform = helpers.PLATFORM
    try:
        opts, args = getopt.getopt(sys.argv[1:], "p:c:", ["platform=", "clubid="])
        for opt, arg in opts:
            if opt == "--platform":
                platform = arg
            elif opt == "--clubid":
                club_id = arg
    except getopt.GetoptError as e:
        print(e)
    asyncio.run(update_matches(club_id, platform))
