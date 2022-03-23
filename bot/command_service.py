import os
from extra import fb, features
from data import api
import data_service
import helpers
from dotenv import load_dotenv


load_dotenv('../.env')
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL = os.getenv('DISCORD_CHANNEL')

CLUB_ID = os.getenv('CLUB_ID')

async def member_stats(msg_content_splitted):
    members = api.get_members()['members']
    reply = "!stats "
    stats_filter = None
    for member in members:
        reply = reply + f"{member['name']} | "
    reply = reply[:-2] + " <skater>|<goalie>|<xfactor>"

    if len(msg_content_splitted) > 1:
        index = data_service.find(members, 'name', msg_content_splitted[1])
        if index:
            stats = members[index]
            if len(msg_content_splitted) > 2:
                stats_filter = msg_content_splitted[2]    
            reply = data_service.format_stats(stats, stats_filter)
    return reply     

async def matches(msg_content_splitted):
    if features.firebase_enabled():
        matches = await fb.find_matches_by_club_id(None)
    else:
        matches = api.get_matches()
    matches = matches + api.get_matches(game_type=api.GAMETYPE.PLAYOFFS.value)
    matches = sorted(matches, key=lambda match: float(match['timestamp']))
    result_string = ""
    if len(msg_content_splitted) > 1:        
        index = data_service.find(matches, 'matchId', msg_content_splitted[1])
        if not index and features.firebase_enabled():
            matches = fb.find_match_by_id(msg_content_splitted[1])
            if matches:
                result_string += helpers.get_match_mark(matches[0]) + data_service.format_result(matches[0]) + "\n"
                result_string += data_service.match_details(matches[0]) + "\n" 
        if index:
            result_string += helpers.get_match_mark(matches[index]) + data_service.format_result(matches[index]) + "\n"
            result_string += data_service.match_details(matches[index]) + "\n" 
    else:
        for i in range(0, len(matches))[-10:]:
            result_string += helpers.get_match_mark(matches[i]) + data_service.format_result(matches[i]) + "\n" 
    return result_string

async def game_record(filter):
    result = ""
    if len(filter) >= 1:
        matches = fb.find_matches_by_club_id(None)
        record = ' '.join(filter)
        records = data_service.game_record(matches, record)
        if records:
            result = f"Single game record for {record}:\n"
            for game_record in records:
                result += helpers.get_match_mark(game_record[1]) + data_service.format_result(game_record[1]) + "\n"
                result += game_record[1]['players'][CLUB_ID][game_record[0]]['playername']+": "
                result += game_record[1]['players'][CLUB_ID][game_record[0]][game_record[2]] + " " + record + "\n"
            
    return result


def match_results2(matches):
    match_results_header = "---\nMatch history:\n"
    if matches:
        match_batches = helpers.chunk_using_generators(matches, 30)                
        for batch in match_batches:
            match_results = ""
            for match in batch:
                match_results += helpers.get_match_mark(match) + data_service.format_result(match) + "\n"
            match_results = match_results_header + match_results
            return match_results
