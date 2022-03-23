from itertools import zip_longest
import interactions
from dotenv import load_dotenv
import os
import jsonmap
import asyncio
import random
import time

load_dotenv('../.env')
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL = os.getenv('DISCORD_CHANNEL')

bot = interactions.Client(token=TOKEN)

all_stats_as_choices = []
for key, value in jsonmap.names.items():
    choice = interactions.Choice(
        name=key,
        value=key,
    )    
    all_stats_as_choices.append(choice)

n=24
stat_choice_chunks=[all_stats_as_choices[i:i + n] for i in range(0, len(all_stats_as_choices), n)]



command_options = []
for i in range(0, len(stat_choice_chunks)):
    option = interactions.Option(
            name=f"stats{i+1}",
            description=f"stats{i+1}",
            type=interactions.OptionType.STRING,
            choices = stat_choice_chunks[i],
    )    
    command_options.append(option)

@bot.command(
    name="stats",
    description="Top stats",
    options = command_options,
)
async def stats(ctx: interactions.CommandContext, stats1="", stats2="", stats3="", stats4="", stats5="", stats6="", stats7="", stats8="", stats9="", stats10=""):
    await ctx.send(f"Hi there!")

for i in range(0, len(stat_choice_chunks)):
    @bot.autocomplete(command="stats", name=f"stats{i+1}")
    async def autocomplete_choice_list(ctx, user_input: str = ""):
        await ctx.populate(stat_choice_chunks[i])

@bot.command(
    name="test",
    description="test",
)
async def test(ctx: interactions.CommandContext):
    await ctx.send(f"Hi there!")


loop = asyncio.get_event_loop()

task1 = loop.create_task(bot._ready())

async def do_stuff_every_x_seconds(timeout, stuff):
    while True:
        await asyncio.sleep(timeout)
        await stuff()

async def stuff():
    await asyncio.sleep(random.random() * 3)
    print(round(time.time(), 1), "Finished doing stuff")
    await bot._http.send_message(900642208942817293, "test")



task2 = loop.create_task(do_stuff_every_x_seconds(5, stuff))

gathered = asyncio.gather(task1, task2)

loop.run_until_complete(gathered)
#bot.start()