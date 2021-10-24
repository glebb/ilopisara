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
            result_string += data_service.format_result(matches[i]) + "\n"
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
            reply = members[index]
            if len(msg_content_splitted) > 2:
                stats_filter = msg_content_splitted[2]    
            stats = data_service.format_stats(reply, stats_filter)
            await message.author.send(stats)
    else:
        await message.channel.send(reply)        

async def handle_matches(message):
    matches = get_matches()
    result_string = ""
    for i in reversed(range(0, len(matches))[-5:]):
        result_string += data_service.format_result(matches[i]) + "\n"
    if result_string:
        await message.channel.send(result_string)


@client.event
async def on_message(message):
    if message.author == client.user:
        return    

    if '!stats' in message.content:
        await handle_member_stats(message)

    if '!matches' in message.content:
        await handle_matches()

client.run(TOKEN)