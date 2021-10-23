import requests
import jsonmap
import time
from cachetools import cached, TTLCache
import os
import discord
from discord.ext import tasks
from dotenv import load_dotenv
import random
import json
from datetime import datetime
import pytz

results = {}
to_zone = pytz.timezone('Europe/Helsinki')


def find(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return None

@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_members():
    print("get_members")
    '''f = open('members.json',)
    data = json.load(f)
    f.close()
    return data'''
    return requests.get('http://localhost:3000/members').json()

@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_matches():
    print("get_matches")
    '''f = open('matches.json',)
    data = json.load(f)
    f.close()
    return data'''
    return requests.get('http://localhost:3000/matches').json()

def print_members(response):
    data = response.json()
    for member in data['members']:
        for k in sorted(member):
            name = jsonmap.get_name(k)
            print(f"{name}: {member[k]}")
        print("")


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

def print_result(match):
    ts = int(match['timestamp'])
    score_time = datetime.fromtimestamp(ts)
    score_time = score_time.astimezone(to_zone).strftime('%d.%m. %H:%M')
    opponentId = match['clubs']['19963']['opponentClubId']
    score_teams = match['clubs']['19963']['details']['name'] + ' - ' + match['clubs'][opponentId]['details']['name']
    score_result = match['clubs']['19963']['scoreString']
    score_string = score_time + ' ' + score_teams + ' ' + score_result + ' '
    return score_string

async def print_stats(author, data, stats_filter):
    message = ""
    for k, v in sorted(data.items()):
        stat = None
        key = jsonmap.get_name(k)
        if stats_filter and key.startswith(stats_filter.lower()):
            stat = key + ': ' + v
        elif not stats_filter:
            if not key.startswith('skater') and not key.startswith('goalie') and not key.startswith('xfactor'):
                stat = key + ': ' + v
        if stat:
            message += stat + "\n"
    if message:
        await author.send(message)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if '!stats' in message.content:
        members = get_members()['members']
        data = "!stats "
        stats_filter = None
        for member in members:
            data = data + f"{member['name']} | "
        data = data[:-2] + " <skater>|<goalie>|<xfactor>"

        split = message.content.split(' ')
        if len(split) > 1:
            index = find(members, 'name', split[1])
            if index:
                data = members[index]
                if len(split) > 2:
                    stats_filter = split[2]    
                await print_stats(message.author, data, stats_filter)
        else:
            await message.channel.send(data)        

    if '!matches' in message.content:
        matches = get_matches()
        result_string = ""
        for i in reversed(range(0, len(matches))[-5:]):
            result_string += print_result(matches[i]) + "\n"
        if result_string:
            await message.channel.send(result_string)

@tasks.loop(seconds = 5)
async def myLoop(channel):
    matches = get_matches()
    result_string = ""
    for i in reversed(range(0, len(matches))):
        match_id = matches[i]['matchId']
        if not match_id in results:
            results[match_id] = matches[i]
            result_string += print_result(matches[i]) + "\n"
    if result_string:
        await channel.send(result_string)

@client.event
async def on_ready():
    # 894334112536625186 murohoki
    # bs 900642208942817293
    channel = client.get_channel(900642208942817293)
    myLoop.start(channel=channel)

client.run(TOKEN)