Discord bot to fetch statistics for EA NHL
Utilizes NHL api's (ONLINE) and local mongo db (DB) to preserve match history with stats.

----------

The story:

2008/10/02 - NHL09 EA Sports Hockey League - murohoki [PS3]: 
"I couldn't wait any longer for someone to come up with a thread like this, so I decided to grab the bunny by the ears and set it up myself.  In short, I've created a club called "murohoki" to gather people interested in NHL09 to play together. The idea is to play "just for fun", but you can cry blood and gnash your teeth if you feel like it. If you are interested, please post your PSN ID here and I will send you an invitation via the game. #murohoki @ IRCnet will also serve as a place where you can express your interest." 
   -p. leikkari https://murobbs.muropaketti.com/posts/1702401461/  

With these words, the story of murohoki began in 2008. It was EA Sports NHL 09 – the first game in the franchise with EASHL mode. It was truly revolutionary and murohoki was there from the beginning! In addition to p. leikkari, aka Yoosef, the original gang included names like zpede, Noddactius, arieli, NSi, bodhi-FIN and Pe-Te, just to name a few. Since then, with every new EA Sports NHL incarnation, murohoki has been present on PSN, at least with some sort of lineup.  

Over the years, most of the players changed, but the original #murohoki IRC-channel kept a certain core group of people together. Some switched from NHL to other online games, while others hardly played at all. Eventually, in 2021, the channel was down to Yoosef, arieli, Noddacitus, zpede and bodhi-FIN. None of us had been actively playing for a while, at least not in murohoki. Few had acquired a PS5 console, and because of the “next-gen” experience, NHL was of some interest again. There were no real plans to play as a team though. "Maybe I play few 1vs1 games, if I get the game at all" I remember thinking at the time.  

One day, just before the release of NHL 22, arieli dropped off from IRC. It didn't attract attention at first, as the channel was mainly for idling anyway. Sometimes days or weeks went by without anyone saying anything. The absence stretched into days, and eventually into weeks. Everyone on the channel pretty much had the same feeling.. Something bad had happened. Arieli had never been off the air for so long. Finally, we ventured to contact arieli's brother via Facebook, from whom we learned that arieli had passed away suddenly because of a medical condition. Although I had never met him face to face, the news was still shocking! After all, we had been in contact with each other for a long time, almost 13 years!   

After recovering from the initial shock, we began to think that it would be nice to honor arieli's memory in some way. The idea quickly came up to get the old gang together for NHL.  After all, that had been the original common denominator for all of us anyways. Since murohoki was still around, and none of us were actively playing, we decided to create a new team and name it as Ilo Pisara, after arieli's player name. This time we were really playing "just for fun", without any further goals (pun intended). We contacted all the old players we could rembmer, and eventually got a team together that included the following murohoki veterans who had played alongside arieli at one point or another:  

Albatrooss  
bodhi-FIN  
HOLYDIVERS  
Lionite  
Noddactius  
Truecorb  
zpede  

Most of us hadn't played EASHL/CHEL in years, but slowly the matches started to get better and better. We agreed to play the PS4 version, as most didn't have the new console yet. The season culminated on 4th of January 2022, when Ilo Pisara won the Division 1 championship after a ten-game winning streak!  Wohoo! 

The time spent with Ilo Pisara was rewarding. There's was a lot of talk about arieli and a lot of reminiscing about the good old days, especially on weekend nights with the help of a few beers. Even though the game itself was the same kind of shit it has been since the beginning, I'm glad I got to share this experience with my old friends. Thanks are due to arieli, although of course the best thing would have been if he had still been around for the games with us. Rest In Peace brother.  

The games will not stop, but one era has ended. Carry on.  

Oh... How is all this related to the Discord bot you might ask? Well, back in the day we used to have IRC-bot to do exactly the same thing as this one does: Show scores, player and teams stats. It is my personal homage to murohoki and arieli. 

----------

Bot (slash) commands:
/results
Show results of latest games from ONLINE

/team <name>
Team record and other details from ONLINE.
Checks also DB for previous matches against this team.

/player <name> <filter>
All stats for player from ONLINE

/top <stat>
Rank club members based on single statistic from ONLINE

/match <id>
Details for specific match from DB.

/record <stat>
Single game record for a stat from DB

The bot will monitor latest results (from DB) and post them to specified channel.

----------

Technical requirements:
* Local mongodb instance, with replica sets setup.
   mongodb.conf:
      replication:
      replSetName: "rs0"
   mongosh: rs.initiate()
* Cronjob to execute db_mongo.py to fetch game results periodically
   0 * * * * cd /home/<user>/ilopisara/ilobotbot && /home/<user>/ilopisara/.venv/bin/python db_mongo.py
* IP that allows access for NHL apis. (test by running py.test)

Copy sample.env as .env and fill all values
Install python requirements: pip install -m requirements.txt

run: python -m ilobot.bot
