import datetime
import sys

import data_service
import db_mongo
import helpers
import nextcord
from ApplicationCommandCog import ApplicationCommandCog
from base_logger import logger
from dacite import from_dict
from data import api
from extra import chatgpt
from models import Match
from nextcord.ext import commands, tasks
from twitch import Twitcher, TwitchStatus

team_name = api.get_team_info(helpers.CLUB_ID)[helpers.CLUB_ID]["name"]
intents = nextcord.Intents.all()


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, intents=intents)
        self.loop.create_task(self.watch_db())
        self.all_teams = ()
        self.fetch_team_names.start()
        self.twitcher = Twitcher()
        self.twitch_check.start()
        # self.check_latest_game.start()
        self.now = None

    async def watch_db(self):
        await self.wait_until_ready()
        logger.info("Watching db...")
        await db_mongo.watch(self.report_results)

    async def report_results(self, match: dict):
        logger.info("Report results to channel")
        channel = self.get_channel(int(helpers.DISCORD_CHANNEL))
        result, details = data_service.match_result(match)
        if result:
            await channel.send((result.discord_print() + "\n" + details)[:1999])
            del match["_id"]
            summary = chatgpt.write_gpt_summary(match)
            await channel.send(summary[:1999])

    def get_team_names(self):
        short_list = list(self.all_teams[-24:])
        try:
            short_list.insert(0, short_list.pop(short_list.index(team_name)))
        except ValueError:
            short_list.insert(0, team_name)
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
        channel = self.get_channel(int(helpers.DISCORD_CHANNEL))
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
            channel = self.get_channel(int(helpers.TWITCH_CHANNEL))
            logger.info(f"Stream activated {self.twitcher.stream_url}")
            await channel.send("Stream started: " + self.twitcher.stream_url)


bot = Bot()
bot.add_cog(ApplicationCommandCog(bot))
bot.run(helpers.TOKEN)
