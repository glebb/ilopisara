import os

import data_service
import db_mongo
import helpers
from data import api
from dotenv import load_dotenv

load_dotenv("../.env")
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL = os.getenv("DISCORD_CHANNEL")

CLUB_ID = os.getenv("CLUB_ID")


async def results(clubId=None):
    matches = await db_mongo.find_matches_by_club_id(clubId)
    result_string = ""
    for i in range(0, len(matches))[-10:]:
        result_string += (
            helpers.get_match_mark(matches[i])
            + data_service.format_result(matches[i])
            + "\n"
        )
    return result_string


async def match(match_id):
    result_string = ""
    matches = await db_mongo.find_match_by_id(match_id)
    if matches:
        result_string += (
            helpers.get_match_mark(matches[0])
            + data_service.format_result(matches[0])
            + "\n"
        )
        result_string += data_service.match_details(matches[0]) + "\n"
    return result_string


async def member_stats(name, stats_filter=None):
    members = api.get_members()["members"]
    reply = ""
    public_reply = ""
    index = data_service.find(members, "name", name)
    if index:
        stats = members[index]
        reply = data_service.format_stats(stats, stats_filter)
        public_reply = "Record: " + members[index]["record"] + "\nRest of the stats delivered by DM."
    return reply, public_reply


async def game_record(stats_filter):
    result = ""
    matches = await db_mongo.find_matches_by_club_id(None)
    temp = " ".join(stats_filter)
    records = data_service.game_record(matches, temp)
    if records:
        result = f"Single game record for {temp}:\n"
        for record in records[:10]:
            result += (
                helpers.get_match_mark(record[1])
                + data_service.format_result(record[1])
                + "\n"
            )
            result += (
                record[1]["players"][CLUB_ID][record[0]]["playername"] + ": "
            )
            result += (
                record[1]["players"][CLUB_ID][record[0]][record[2]]
                + " "
                + record
                + "\n"
            )
    return result


def match_results2(matches):
    match_results_header = "---\nMatch history:\n"
    if matches:
        match_batches = helpers.chunk_using_generators(matches, 30)
        for batch in match_batches:
            match_results_string = ""
            for match_result in batch:
                match_results_string += (
                    helpers.get_match_mark(match_result)
                    + data_service.format_result(match_result)
                    + "\n"
                )
            match_results_string = match_results_header + match_results_string
            return match_results_string


async def team_record(name):
    result_string = ""
    temp = api.get_team_record(name)
    record = data_service.team_record(temp)
    if record:
        result_string += record + "\n"
        club_id = list(temp.keys())[0]
        members = api.get_members(club_id)
        if club_id != CLUB_ID:
            matches = await db_mongo.find_matches_by_club_id(club_id)
        else:
            matches = None
        top_stats = data_service.top_stats(members["members"], "points per game")
        if top_stats:
            top_reply = "---\n" + top_stats
        else:
            top_reply = "---\n" + "No top stats available"
        result_string += top_reply
        if matches:
            match_results = match_results2(matches)
            if match_results:
                result_string += match_results
    return result_string
