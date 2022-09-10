import asyncio
import os

import motor.motor_asyncio
import pymongo.errors
from base_logger import logger
from data import api
from dotenv import load_dotenv

client = motor.motor_asyncio.AsyncIOMotorClient()
db = client.ilo

load_dotenv("../.env")
DISCORD_CHANNEL = int(os.getenv("DISCORD_CHANNEL"))


async def watch(bot):
    resume_token = None
    pipeline = [{"$match": {"operationType": "insert"}}]
    try:
        async with db.matches.watch(pipeline) as stream:
            async for insert_change in stream:
                await bot.report_results(insert_change["fullDocument"])
                resume_token = stream.resume_token
    except pymongo.errors.PyMongoError:
        if resume_token is None:
            logger.error("Database connection is fucked, cannot watch for updates")
        else:
            async with db.matches.watch(pipeline, resume_after=resume_token) as stream:
                async for insert_change in stream:
                    await bot.report_results(insert_change["fullDocument"])


async def update_matches():
    new_matches = []
    for game_type in api.GAMETYPE:
        matches = api.get_matches(count=50, game_type=game_type.value)
        for match in matches:
            match["gameType"] = game_type.value
            update_result = await db.matches.update_one(
                {"matchId": match["matchId"]}, {"$setOnInsert": match}, upsert=True
            )
            if update_result.matched_count == 0:
                new_matches.append(match)
    return new_matches


async def find_matches_by_club_id(versusClubId=None):
    matches = (
        db.matches.find({f"clubs.{versusClubId}": {"$exists": True}})
        if versusClubId
        else db.matches.find()
    )
    return sorted(
        await matches.to_list(length=10000),
        key=lambda match: float(match["timestamp"]),
    )


async def find_match_by_id(matchId):
    matches = db.matches.find({"matchId": matchId})
    return await matches.to_list(length=1)


if __name__ == "__main__":
    asyncio.run(update_matches())
