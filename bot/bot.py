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

@cached(cache=TTLCache(maxsize=1024, ttl=120))
def get_members():
    print("get_members")
    f = open('members.json',)
    data = json.load(f)
    f.close()
    return data
    #return requests.get('http://localhost:3000/members')

@cached(cache=TTLCache(maxsize=1024, ttl=120))
def get_matches():
    '''print("get_matches")
    f = open('matches.json',)
    data = json.load(f)
    f.close()
    return data'''
    return requests.get('http://localhost:3000/matches')

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

#intents = discord.Intents().all()
#intents=intents
client = discord.Client()

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if '!stats' in message.content:
        await message.author.send("Haista vittu.")
        '''members = get_members().json()['members']
        data = "!stats <name>: "
        for member in members:
            data = data + f"{member['name']} "

        split = message.content.split(' ')
        if len(split) > 1:
            index = find(members, 'name', split[1])
            if index:
                data = members[index]
        await message.author.send(str(data).strip()[:2000])'''

@tasks.loop(seconds = 5)
async def myLoop(channel):
    matches = get_matches().json()
    for i in reversed(range(0, len(matches))):
        match_id = matches[i]['matchId']
        if not match_id in results:
            results[match_id] = matches[i]
            ts = int(matches[i]['timestamp'])
            score_time = datetime.fromtimestamp(ts)
            score_time = score_time.astimezone(to_zone).strftime('%d.%m. %H:%M')
            opponentId = matches[i]['clubs']['19963']['opponentClubId']
            score_teams = matches[i]['clubs']['19963']['details']['name'] + ' - ' + matches[i]['clubs'][opponentId]['details']['name']
            score_result = matches[i]['clubs']['19963']['scoreString']
            score_string = score_time + ' ' + score_teams + ' ' + score_result + ' '
            await channel.send(score_string)

@client.event
async def on_ready():
    channel = client.get_channel(894334112536625186)
    myLoop.start(channel=channel)

client.run(TOKEN)