import os
import discord
from discord.ext import tasks
from dotenv import load_dotenv
from data import get_matches, get_members
import data_service

match_results_storage = {}

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL = os.getenv('DISCORD_CHANNEL')
client = discord.Client()

@tasks.loop(seconds = 5)
async def myLoop(channel):
    matches = get_matches()
    result_string = ""
    for i in reversed(range(0, len(matches))):
        match_id = matches[i]['matchId']
        if not match_id in match_results_storage:
            match_results_storage[match_id] = matches[i]
            if len(match_results_storage) > 5:
                result_string += data_service.format_result(matches[i]) + "\n"
                result_string += data_service.match_details(matches[i]) + "\n"
    if result_string:
        await channel.send(result_string)

@client.event
async def on_ready():
    channel = client.get_channel(int(CHANNEL))
    myLoop.start(channel=channel)

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
        result_string += data_service.format_result(matches[index]) + "\n"
        result_string += data_service.match_details(matches[index]) + "\n" 
    else:
        for i in reversed(range(0, len(matches))[-5:]):
            result_string += data_service.format_result(matches[i]) + "\n" 
    if result_string:
        await message.channel.send(result_string)

async def handle_top_stats(message):
    command, *filter = message.content.split(' ')
    if len(filter) >= 1:
        members = get_members()['members']
        result = data_service.top_stats(members, ' '.join(filter))
        if result:
            await message.channel.send(result)

@client.event
async def on_message(message):
    if message.author == client.user:
        return    

    if '!stats' in message.content:
        await handle_member_stats(message)

    if '!matches' in message.content:
        await handle_matches(message)

    if '!top' in message.content:
        await handle_top_stats(message)

client.run(TOKEN)