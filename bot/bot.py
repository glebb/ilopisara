import os
import discord
from discord.ext import tasks
from dotenv import load_dotenv
from data import get_matches, get_members, get_team_record
import data_service
import jsonmap
import twitch
import giphy

match_results_storage = {}

load_dotenv('../.env')
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL = os.getenv('DISCORD_CHANNEL')

client = discord.Client()

@tasks.loop(seconds = 5)
async def latest_results(channel):
    matches = get_matches()
    result_string = ""
    for i in reversed(range(0, len(matches))):
        match_id = matches[i]['matchId']
        if not match_id in match_results_storage:
            match_results_storage[match_id] = matches[i]
            if len(match_results_storage) > 5:
                scores = matches[i]['clubs'][os.getenv('CLUB_ID')]['scoreString'].split(' - ')
                if int(scores[0]) > int(scores[1]):
                    gif = giphy.get_win()
                else:
                    gif = giphy.get_fail()
                await channel.send(data_service.format_result(matches[i]))
                await channel.send(gif)
                await channel.send(data_service.match_details(matches[i]))

@tasks.loop(seconds = 15)
async def twitch_poller(channel):
    stream = twitch.get_live_stream()
    if stream and stream['status'] == 'start':
        await channel.send("Stream started: " +stream['url'])

@client.event
async def on_ready():
    if CHANNEL:
        channel = client.get_channel(int(CHANNEL))
        latest_results.start(channel=channel)
    if os.getenv('TWITCH_CLIENT_ID') and CHANNEL:
        twitch_poller.start(channel=channel)

async def handle_member_stats(message):
    msg_content_splitted = message.content.split(' ')
    members = get_members()['members']
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
        await message.channel.send(reply)        

async def handle_matches(message):
    msg_content_splitted = message.content.split(' ')
    matches = get_matches()
    result_string = ""
    if len(msg_content_splitted) > 1:
        index = data_service.find(matches, 'matchId', msg_content_splitted[1])
        if index:
            result_string += data_service.format_result(matches[index]) + "\n"
            result_string += data_service.match_details(matches[index]) + "\n" 
    else:
        for i in reversed(range(0, len(matches))[-5:]):
            result_string += data_service.format_result(matches[i]) + "\n" 
    if result_string:
        await message.channel.send(result_string)

async def handle_top_stats(message):
    command, *filter = message.content.split(' ')
    result = None
    if len(filter) >= 1:
        members = get_members()['members']
        result = data_service.top_stats(members, ' '.join(filter))
        if result:
            await message.channel.send(result)
    if not result:
        await message.author.send("Try some of these:\n" + " \n".join(list(sorted(jsonmap.names.values()))[:100]))
        await message.author.send(" \n".join(list(sorted(jsonmap.names.values()))[100:]))

async def handle_team_record(message):
    command = message.content.split(' ')
    if len(command) < 2:
        await message.channel.send("!team <team_name>")
    else:
        team = " ".join(command[1:])
        await message.channel.send("Getting records for " + team + "\n" + "Please wait...")
        data = get_team_record(team)
        team_record = data_service.team_record(data)
        if team_record:
            clubId = list(data.keys())[0]
            members = get_members(clubId)
            top_stats = data_service.top_stats(members['members'], "points per game")
            if top_stats:
                top_reply = "---\nTop points per game players:\n" + top_stats
            else:
                top_reply = "No top stats available"
            await message.channel.send(team_record)
            await message.channel.send(top_reply)

        else:
            await message.channel.send("Something went wrong. Try again after few minutes. Also check team name is correct: " + team)

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

client.run(TOKEN)