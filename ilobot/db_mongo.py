# pylint: disable=C0413

import asyncio
import getopt
import sys

import motor.motor_asyncio
import pymongo.errors
from cachetools import TTLCache, cached
from dacite import MissingValueError, from_dict

import ilobot.config
from ilobot import db_utils, helpers
from ilobot.base_logger import logger
from ilobot.config import DB_NAME, CLUB_ID
from ilobot.data import api
from ilobot.models import Match

client = motor.motor_asyncio.AsyncIOMotorClient(serverSelectionTimeoutMS=100)
db = client[DB_NAME]


def handle_exceptions(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except pymongo.errors.PyMongoError as e:
            logger.exception(f"DB not accessible: {e}")
            return None

    return wrapper


@handle_exceptions
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


@handle_exceptions
async def update_matches(team_id, system):
    for game_type in helpers.GAMETYPE:
        postfix = ""
        if team_id != ilobot.config.CLUB_ID:
            postfix = "_" + team_id + "_" + system
        matches = api.get_matches(
            club_id=team_id, platform=system, count=10, game_type=game_type.value
        )
        for match in reversed(matches):
            if len(match["aggregate"]) != 2:
                continue
            await db["replica" + postfix].update_one(
                {"matchId": match["matchId"]}, {"$setOnInsert": match}, upsert=True
            )
            try:
                enriched_match = db_utils.enrich_match(match, game_type)
            except Exception as e:
                logger.exception(f"Could not enrich matchId {match['matchId']}: {e}")
                continue
            try:
                from_dict(data_class=Match, data=enriched_match)
                logger.info(f"Successfully parsed match {enriched_match['matchId']}")
            except MissingValueError:
                logger.exception(f"Error parsing match {enriched_match['matchId']}")
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


@handle_exceptions
async def find_matches_by_club_id(
    versus_club_id=None, game_type=None, player_name=None, db_name=DB_NAME
):
    db = client[db_name]
    query = {}
    if game_type:
        query["gameType"] = game_type
    if player_name:
        query["player_names"] = {"$elemMatch": {"name": player_name}}
    if versus_club_id:
        query["opponent.id"] = versus_club_id
    matches = db.matches.find(query).sort("timestamp", 1)
    return await matches.to_list(length=10000)


async def find_match_by_id(match_id):
    matches = db.matches.find({"matchId": match_id})
    return await matches.to_list(length=1)


@handle_exceptions
@cached(cache=TTLCache(maxsize=1024, ttl=180))
async def get_known_team_names():
    temp = db.opponents.find({}, {"name": 1})
    data = await temp.to_list(length=10000)
    return map(lambda x: x["name"], data)


@handle_exceptions
async def get_sorted_matches(sort_key):
    matches = (
        db.matches.find()
        .sort(sort_key, -1)
        .collation({"locale": "en", "numericOrdering": True})
    )
    return await matches.to_list(length=10000)


@handle_exceptions
async def find_matches_for_player(player_id):
    matches = db.matches.find(
        {f"players.{ilobot.config.CLUB_ID}.{player_id}": {"$exists": True}}
    ).sort("timestamp", 1)
    return await matches.to_list(length=10000)


@handle_exceptions
async def get_latest_match(count=1):
    matches = db.matches.find().sort("timestamp", -1)
    return await matches.to_list(count)


@handle_exceptions
async def find_recent_matches(club_id=None, game_type=None, source=None, limit=20):
    """Find recent matches with optional filters using aggregation pipeline.
    
    Args:
        club_id: Optional club ID to filter by
        game_type: Optional game type to filter by
        source: Optional source/match type to filter by
        limit: Maximum number of matches to return (default 20)
        
    Returns:
        List of matches sorted by timestamp (newest first)
    """
    pipeline = [
        {"$match": {}},
        {"$sort": {"timestamp": -1}},
        {"$limit": limit}
    ]
    
    match_conditions = {}
    if club_id:
        match_conditions["opponent.id"] = club_id
    if game_type:
        match_conditions["gameType"] = game_type
    if source:
        match_conditions[f"clubs.{CLUB_ID}.matchType"] = source
    
    if match_conditions:
        pipeline[0]["$match"] = match_conditions
    
    matches = await db.matches.aggregate(pipeline).to_list(limit)
    return list(reversed(matches))


if __name__ == "__main__":
    club_id = ilobot.config.CLUB_ID
    platform = ilobot.config.PLATFORM
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
