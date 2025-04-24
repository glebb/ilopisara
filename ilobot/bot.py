import datetime
import pprint
import sys
from typing import cast

import nextcord
from dacite import from_dict
from nextcord.ext import commands, tasks

import ilobot.config
from ilobot import command_service, data_service, db_mongo, tumblrl
from ilobot.base_logger import logger
from ilobot.data import api
from ilobot.extra import chatgpt
from ilobot.twitch import Twitcher, TwitchStatus

from .models import Match


class Bot(commands.Bot):
    TEAM_NAME = api.get_team_info(ilobot.config.CLUB_ID)[ilobot.config.CLUB_ID]["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, intents=nextcord.Intents.all())
        self.player_names = {}
        self.loop.create_task(self.watch_db())
        self.all_teams = ()
        self.fetch_team_names.start()
        self.twitcher = Twitcher()
        self.twitch_check.start()
        # self.check_latest_game.start()
        self.now = None
        self.pre_fetch_players_for_caching()

    def pre_fetch_players_for_caching(self):
        for member in api.get_members():
            member = api.get_member(member["name"])
            self.player_names[member["name"]] = member.get(
                "skplayername", member["name"]
            )
        logger.info(f"Team: {ilobot.config.CLUB_ID} - {self.TEAM_NAME}")
        logger.info("Players: \n" + pprint.pformat(self.player_names))

    async def watch_db(self):
        await self.wait_until_ready()
        logger.info("Watching db...")
        await db_mongo.watch(self.report_results)

    async def report_results(self, match: dict):
        logger.info("Report results to channel")
        channel: nextcord.PartialMessageable = cast(
            nextcord.PartialMessageable,
            self.get_channel(int(ilobot.config.DISCORD_CHANNEL)),
        )
        result, details = data_service.match_result(match)
        if result:
            response, matches = await command_service.team_record(
                result.opponent_name, ilobot.config.PLATFORM
            )
            response = "" if not response else response
            history = [
                (data_service.format_result(m).as_chatgpt_history())
                for m in await db_mongo.get_latest_match(30)
            ]
            db_id = match.pop("_id")

            vs_matches = await db_mongo.find_matches_by_club_id(match["opponent"]["id"])
            summary: str = (
                await chatgpt.write_gpt_summary(
                    match, history[1:], vs_matches[1:]
                )  # history[0] is same as match
                if "summary" not in match
                else match["summary"]
            )

            await channel.send((result.discord_print() + "\n" + details)[:1999])
            if summary:
                if "summary" not in match:
                    await db_mongo.db.matches.update_one(
                        {"_id": db_id}, {"$set": {"summary": summary}}
                    )
                await channel.send(
                    ("\n\nYoosef's analysis\n" + summary + "\n\n")[:1999]
                )
                tumblrl.post(
                    summary,
                    title=str(result),
                    tags=["nhl24"],
                )
            if len(matches) > 1:
                matches.pop()
                response += "\nMatch history:\n"
                response += "\n".join([line.discord_print() for line in matches])
            await channel.send(response[:1999] + "\n\n")

    def get_team_names(self):
        short_list = list(self.all_teams[-24:])
        try:
            short_list.insert(0, short_list.pop(short_list.index(self.TEAM_NAME)))
        except ValueError:
            short_list.insert(0, self.TEAM_NAME)
        except:
            logger.error("Unexpected error:", sys.exc_info()[0])
            raise
        return tuple(short_list)

    @tasks.loop(minutes=10)
    async def check_latest_game(self):
        await self.wait_until_ready()
        if not 19 <= datetime.datetime.now().hour < 22:
            return
        if self.now and self.now + 3600 * 36 > datetime.datetime.now().timestamp():
            return
        channel = self.get_channel(int(ilobot.config.DISCORD_CHANNEL))
        logger.info("Checking latest game timestamp")
        latest_game = await db_mongo.get_latest_match()
        if latest_game is None:
            logger.info("No latest game found")
            return
        latest_game_timestamp = int(
            from_dict(data_class=Match, data=latest_game[0]).timestamp
        )
        if not self.now:
            self.now = latest_game_timestamp
            return

        if latest_game_timestamp + 3600 * 36 < datetime.datetime.now().timestamp():
            self.now = datetime.datetime.now().timestamp()
            await channel.send(
                f"It's been {round((self.now - latest_game_timestamp) / 3600) } "
                "hours since the last game, time to play @here?"
            )

    @tasks.loop(minutes=10)
    async def fetch_team_names(self):
        self.all_teams = tuple(await db_mongo.get_known_team_names())

    @tasks.loop(minutes=2)
    async def twitch_check(self):
        await self.wait_until_ready()

        status = self.twitcher.update()
        if status == TwitchStatus.STOPPED:
            return
        if status == TwitchStatus.STARTED:
            channel = self.get_channel(int(ilobot.config.TWITCH_CHANNEL))
            logger.info(f"Stream activated {self.twitcher.stream_url}")
            await channel.send("Stream started: " + self.twitcher.stream_url)
