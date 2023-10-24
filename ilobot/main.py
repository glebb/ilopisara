from ilobot import helpers
from ilobot.bot import Bot
from ilobot.cogs import ApplicationCommandCog


def main():
    bot = Bot()
    bot.add_cog(ApplicationCommandCog(bot))
    bot.run(helpers.TOKEN)


if __name__ == "__main__":
    main()
