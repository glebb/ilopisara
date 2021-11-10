Discord bot to fetch statistics for EA NHL 22

!stats player [<skater>|<goalie>|<xfactor>]
All stats for specific player

!matches <matchId> (match details)
Last 5 matches or details for specific match

!top statistic (e.g. 'hits per game')
Rank club members based on single statistic

!team team name (e.g. ilo pisara)
Team record and other details

The bot will periodically check latest results and post them to specified channel

place .env file in root with following content
PLATFORM=
CLUB_ID=
USE_PROXY=0
DISCORD_TOKEN=
DISCORD_CHANNEL=
TWITCH_CLIENT_ID=
TWITCH_OAUTH=
TWITCH_STREAMERS=
GIPHY_API_KEY=

run bot:
pip install -m requirements.txt
python bot.py

Sometimes the api's require additional auth stuff,
then use proxy and start the node app, which uses puppeteer.

run proxy:
npm i
node app

To get puppeteer running in AWS Bitnami Node/Express ec2 image:
sudo sysctl -w kernel.unprivileged_userns_clone=1
sudo apt install -y gconf-service libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget libgbm1
