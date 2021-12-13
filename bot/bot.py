import os
import discord
from discord.ext import tasks
from dotenv import load_dotenv
from data import api
import data_service
import jsonmap
from extra import fb, giphy, twitch, features

match_results_storage = {}

load_dotenv('../.env')
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL = os.getenv('DISCORD_CHANNEL')

CLUB_ID = os.getenv('CLUB_ID')

client = discord.Client()
single_channel = None

def is_win(match):
    scores = match['clubs'][os.getenv('CLUB_ID')]['scoreString'].split(' - ')
    return int(scores[0]) > int(scores[1])

def get_match_mark(match):
    if is_win(match):
        mark = ":white_check_mark: "
    else:
        mark = ":x: "
    return mark

@tasks.loop(seconds = 15)
async def latest_results(channel):
    if len(match_results_storage) == 0:
        initial = True
    else:
        initial = False
    regularmatches = api.get_matches()
    playoffs = api.get_matches(game_type=api.GAMETYPE.PLAYOFFS.value)
    matches = regularmatches + playoffs
    matches = sorted(matches, key=lambda match: float(match['timestamp']))
    for i in reversed(range(0, len(matches))):
        match_id = matches[i]['matchId']
        if not match_id in match_results_storage:
            match_results_storage[match_id] = matches[i]
            if features.firebase_enabled():
                if matches[i] in regularmatches:
                    game_type = 'matches'
                else:
                    game_type = 'playoffs'
                fb.save_match(matches[i], game_type)
            if not initial:
                if is_win(matches[i]):
                    mark = ":white_check_mark: "
                    gif = giphy.get_win()
                else:
                    mark = ":x: "
                    gif = giphy.get_fail()
                await channel.send(mark + data_service.format_result(matches[i]))
                await channel.send(gif)
                await channel.send(data_service.match_details(matches[i]))

@tasks.loop(seconds = 15)
async def twitch_poller(channel):
    stream = twitch.get_live_stream()
    if stream and stream['status'] == 'start':
        await channel.send("Stream started: " +stream['url'])

@client.event
async def on_ready():
    global single_channel
    single_channel = client.get_channel(int(os.getenv('SINGLE_CHANNEL')))
    if CHANNEL:
        channel = client.get_channel(int(CHANNEL))
        latest_results.start(channel=channel)
    if os.getenv('TWITCH_CLIENT_ID') and CHANNEL:
        twitch_poller.start(channel=channel)

async def handle_member_stats(message):
    msg_content_splitted = message.content.split(' ')
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
            await message.author.send(reply)
    else:
        await single_channel.send(reply)        

async def handle_matches(message):
    msg_content_splitted = message.content.split(' ')
    matches = api.get_matches()
    matches = matches + api.get_matches(game_type=api.GAMETYPE.PLAYOFFS.value)
    matches = sorted(matches, key=lambda match: float(match['timestamp']))
    result_string = ""
    if len(msg_content_splitted) > 1:        
        index = data_service.find(matches, 'matchId', msg_content_splitted[1])
        if not index and features.firebase_enabled():
            matches = fb.find_match_by_id(msg_content_splitted[1])
            if matches:
                result_string += get_match_mark(matches[index]) + data_service.format_result(matches[0]) + "\n"
                result_string += data_service.match_details(matches[0]) + "\n" 
        if index:
            result_string += get_match_mark(matches[index]) + data_service.format_result(matches[index]) + "\n"
            result_string += data_service.match_details(matches[index]) + "\n" 
    else:
        for i in range(0, len(matches))[-10:]:
            result_string += get_match_mark(matches[i]) + data_service.format_result(matches[i]) + "\n" 
    if result_string:
        await single_channel.send(result_string)

async def handle_top_stats(message):
    command, *filter = message.content.split(' ')
    result = None
    if len(filter) >= 1:
        members = api.get_members()['members']
        result = data_service.top_stats(members, ' '.join(filter))
        if result:
            await single_channel.send(result)
    if not result:
        await message.author.send("Try some of these:\n" + " \n".join(list(sorted(jsonmap.names.values()))[:100]))
        await message.author.send(" \n".join(list(sorted(jsonmap.names.values()))[100:]))

def chunk_using_generators(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

async def handle_team_record(message):
    command = message.content.split(' ')
    if len(command) < 2:
        await single_channel.send("!team <team_name>")
    else:
        team = " ".join(command[1:])
        await single_channel.send("Getting records for " + team + "\n" + "Please wait...")
        temp = api.get_team_record(team)
        team_record = data_service.team_record(temp)
        if team_record:
            clubId = list(temp.keys())[0]
            members = api.get_members(clubId)
            if features.firebase_enabled() and clubId != CLUB_ID:
                matches = fb.find_matches_by_club_id(clubId)
            else:
                matches = None
            top_stats = data_service.top_stats(members['members'], "points per game")
            if top_stats:
                top_reply = "---\nTop points per game players:\n" + top_stats
            else:
                top_reply = "No top stats available"
            await single_channel.send(team_record)
            await single_channel.send(top_reply)
            match_results_header = "---\nMatch history:\n"
            if matches:
                match_batches = chunk_using_generators(matches, 30)                
                for batch in match_batches:
                    match_results = ""
                    for match in batch:
                        match_results += get_match_mark(match) + data_service.format_result(match) + "\n"
                    match_results = match_results_header + match_results
                    await single_channel.send(match_results)                
        else:
            await single_channel.send("Something went wrong. Try again after few minutes. Also check team name is correct: " + team)

async def handle_history(message):
    matches = fb.find_matches_by_club_id(None)
    match_batches = chunk_using_generators(matches, 25)                
    match_results_header = "---\nMatch history:\n"
    for batch in match_batches:
        match_results = ""
        for match in batch:
            match_results += get_match_mark(match) + data_service.format_result(match) + "\n"
        match_results = match_results_header + match_results
        await message.author.send(match_results)


@client.event
async def on_message(message):
    if message.author == client.user:
        return    

    if '!stats' in message.content:
        await handle_member_stats(message)

    elif '!matches' in message.content:
        await handle_matches(message)

    elif '!top' in message.content:
        await handle_top_stats(message)

    elif '!team' in message.content:
        await handle_team_record(message)

    elif '!history' in message.content and features.firebase_enabled():
        await handle_history(message)


client.run(TOKEN)