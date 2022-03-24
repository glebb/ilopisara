import interactions
from dotenv import load_dotenv
import os
from ibot_tasks import get_latest_results
from ibot_commands import create_top_command, create_team_command, create_matches_command, create_stats_command, create_record_command
import asyncio
import ibot_commands

load_dotenv("../.env")
TOKEN = os.getenv("DISCORD_TOKEN")

client = interactions.Client(token=TOKEN)
ibot_commands.client = client

create_top_command(client)
create_team_command(client)
create_matches_command(client)
create_stats_command(client)
create_record_command(client)

async def do_stuff_every_x_seconds(timeout, stuff):
    while True:
        await asyncio.sleep(timeout)
        await stuff(client)


event_loop = asyncio.get_event_loop()
bot_task = event_loop.create_task(client._ready())
get_results_task = event_loop.create_task(do_stuff_every_x_seconds(30, get_latest_results))
all_tasks = asyncio.gather(bot_task, get_results_task)
event_loop.run_until_complete(all_tasks)

