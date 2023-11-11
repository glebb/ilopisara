from ilobot import config
from ilobot.bot import Bot
from ilobot.cogs import ApplicationCommandCog


def main():
    bot = Bot()
    bot.add_cog(ApplicationCommandCog(bot))
    bot.run(config.DISCORD_TOKEN)


if __name__ == "__main__":
    main()
