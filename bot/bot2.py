import nextcord
import os
from base_logger import logger
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from dotenv import load_dotenv

load_dotenv("../.env")
GUILD_ID = int(os.getenv("GUILD_ID"))
TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot()

@bot.slash_command(guild_ids=[GUILD_ID])
async def team(
    interaction: Interaction,
    name: str = SlashOption(
        name = "name",
        description="Team name",
    ),
):
    await interaction.response.send_message(f"Stats for {name}")

@bot.slash_command(guild_ids=[GUILD_ID])
async def matches(
    interaction: Interaction,
):
    await interaction.response.send_message(f"Show results of latest matches")


@bot.slash_command(guild_ids=[GUILD_ID])
async def top(
    interaction: Interaction,
    stats_name: str = SlashOption(
        name = "stats_name",
        description="Stats name (e.g. points)",
    ),    
):
    await interaction.response.send_message(f"Show top stats")

@bot.slash_command(guild_ids=[GUILD_ID])
async def player(
    interaction: Interaction,
    name: str = SlashOption(
        name = "name",
        description="Player name",
    ),    
):
    await interaction.response.send_message(f"Show stats for player")

@bot.slash_command(guild_ids=[GUILD_ID])
async def record(
    interaction: Interaction,
    stats_name: str = SlashOption(
        name = "stats_name",
        description="Game specific record for a stat (e.g. goals)",
    ),    
):
    await interaction.response.send_message(f"Show gamerecord for a stat")


""""
@your_favorite_dog.on_autocomplete("dog")
async def favorite_dog(interaction: Interaction, dog: str):
    if not dog:
        # send the full autocomplete list
        await interaction.response.send_autocomplete(list(names.values())[:25])
        return
    # send a list of nearest matches from the list of dog breeds
    get_near_dog = [breed for breed in list(names.values()) if breed.lower().startswith(dog.lower())]
    await interaction.response.send_autocomplete(get_near_dog[:25])
"""
bot.run(TOKEN)