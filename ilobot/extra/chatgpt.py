import datetime
import random

from dacite import from_dict
from openai import AsyncOpenAI, OpenAIError

from ilobot import config, data_service, helpers, jsonmap
from ilobot.base_logger import logger
from ilobot.config import CLUB_ID, GPT_MODEL, OPEN_API
from ilobot.data import api
from ilobot.extra.format import format_game_data
from ilobot.helpers import is_overtime
from ilobot.models import Match, MatchType

SKIP_KEYS = (
    "matchId",
    "timeAgo",
    "player_names",
    "toa",
    "raw",
    "teamArtAbbr",
    "opponentTeamArtAbbr",
    "dnf",
    "passc",
    "passa",
    "customKit",
    "teamId",
    "opponentTeamId",
    "OnlineGameType",
    "asset",
    "rank",
    "gameType",
    "clubDivision",
    "memberString",
    "posSorted",
    "timestamp",
    "opponent",
    "playerLevel",
    "platform",
    "losses",
)

SKIP_PLAYER_KEYS = (
    "removedReason",
    "result",
    "score",
    "scoreRaw",
    "scoreString",
    "teamSide",
    "platform",
)

KEY_MAPPINGS = {
    "opponentClubId": "Opponent Club ID",
    "name": "Club name",
}


def handle_keys(data, game_type=None):
    """Skip unwanted keys and convert rest to mapped names"""
    if not game_type:
        game_type = int(data["clubs"][CLUB_ID]["cNhlOnlineGameType"])
    converted_data = {}
    for key, value in data.items():
        original_key = key

        for skip_key in SKIP_KEYS:
            if skip_key in key:
                original_key = None
        if not original_key:
            continue

        # skip power play stats for 3vs3
        if key in ("ppo", "ppg", "skppg") and game_type >= 200:
            continue

        if key.startswith("sk"):  # skip skater stats if goalie
            if data["position"] == "goalie":
                continue
        if (
            key.startswith("skfo") and data["position"] != "center"
        ):  # skip faceoff stats if not center
            continue
        if key.startswith("gl"):  # skip goalie stats if not goalie
            if data["position"] != "goalie":
                continue

        if "position" in data:  # player data
            if key in SKIP_PLAYER_KEYS:
                continue
            if key == "class":
                value = helpers.LOADOUTS.get(value, value)

        if isinstance(value, dict):
            # Recursively process nested dictionaries
            converted_data[original_key] = handle_keys(value, game_type)
        elif key in KEY_MAPPINGS:
            # If key is in the mappings, replace it with the full name
            converted_data[KEY_MAPPINGS[key]] = value
        elif key in jsonmap.names:
            # If key is in the mappings, replace it with the full name
            converted_data[jsonmap.names[key]] = value
        else:
            converted_data[key] = value
    return converted_data


def chatify_data(game: dict, skip_player_names=False):
    cleaned_data = handle_keys(game)

    # Get team analysis for each club
    for key in cleaned_data["clubs"].keys():
        # Get team name from club data
        team_name = cleaned_data["clubs"][key]["details"]["Club name"]

        # Get team stats from API
        team_data = api.get_team_record(team_name, config.PLATFORM)
        if team_data:
            api_key = list(team_data.keys())[0]
            record = list(map(int, team_data[api_key]["record"].split("-")))
            total_games = sum(record)

            if total_games > 0:
                # Calculate all stats
                stats = {
                    "record": {
                        "wins": record[0],
                        "losses": record[1],
                        "otl": record[2],
                        "total_games": total_games,
                        "win_pct": round(record[0] / total_games * 100, 1),
                        "points_pct": round(
                            (record[0] * 2 + record[2]) / (total_games * 2) * 100, 1
                        ),
                    },
                    "scoring": {
                        "goals_for": int(team_data[api_key]["goals"]),
                        "goals_against": int(team_data[api_key]["goalsAgainst"]),
                        "goals_per_game": round(
                            int(team_data[api_key]["goals"]) / total_games, 2
                        ),
                        "goals_against_per_game": round(
                            int(team_data[api_key]["goalsAgainst"]) / total_games, 2
                        ),
                        "goal_differential": int(team_data[api_key]["goals"])
                        - int(team_data[api_key]["goalsAgainst"]),
                        "goal_differential_per_game": round(
                            (
                                int(team_data[api_key]["goals"])
                                - int(team_data[api_key]["goalsAgainst"])
                            )
                            / total_games,
                            2,
                        ),
                    },
                    "team_info": {
                        "division": int(team_data[api_key]["currentDivision"]),
                        "rank": int(team_data[api_key].get("rank", 0)),
                        "streak": team_data[api_key].get("streak", "N/A"),
                        "last_ten": team_data[api_key].get("last_ten", "N/A"),
                    },
                }

                # Format stats as markdown-friendly strings
                team_analysis = [
                    f"record: {stats['record']['wins']}-{stats['record']['losses']}-{stats['record']['otl']} ({stats['record']['win_pct']}% wins, {stats['record']['points_pct']}% points)",
                    f"scoring: {stats['scoring']['goals_per_game']} GF/{stats['scoring']['goals_against_per_game']} GA per game ({stats['scoring']['goal_differential_per_game']:+.2f} diff)",
                    f"totals: {stats['scoring']['goals_for']} GF/{stats['scoring']['goals_against']} GA ({stats['scoring']['goal_differential']:+} diff)",
                    f"division: {stats['team_info']['division']} | rank: {stats['team_info']['rank']} | streak: {stats['team_info']['streak']} | last10: {stats['team_info']['last_ten']}",
                ]

                # Add the analysis to the club data
                cleaned_data["clubs"][key]["team_analysis"] = team_analysis
                cleaned_data["clubs"][key][
                    "team_stats"
                ] = stats  # Raw stats for potential deeper analysis

        # Add player data
        cleaned_data["clubs"][key]["players"] = cleaned_data["players"][key]
        #    cleaned_data["clubs"][key]["players"] = {}
        cleaned_data["clubs"][key]["no_game"] = check_no_game(game)

    clubs = {}
    for club_id, club_data in cleaned_data["clubs"].items():
        # convert club id to club name
        club_name = club_data["details"]["Club name"]
        clubs[club_name] = club_data
        clubs[club_name]["hits"] = game["aggregate"][club_id]["skhits"]
        clubs[club_name]["clubId"] = club_id
        del clubs[club_name]["details"]

        # add player actual names under the club data
        # if not skip_player_names:
        clubs[club_name]["players"] = {
            (
                player_data["playername"]
                if skip_player_names
                else api.get_member(player_data["playername"]).get(
                    "skplayername", player_data["playername"]
                )
                or player_data["playername"]
            ): player_data
            for player_id, player_data in club_data["players"].items()
        }
        for player in clubs[club_name]["players"]:
            clubs[club_name]["players"][player]["playername"] = player

    del cleaned_data["players"]
    cleaned_data["clubs"] = clubs
    match = from_dict(data_class=Match, data=game)
    overtime = is_overtime(match)
    if overtime:
        cleaned_data["overtime"] = True
    else:
        cleaned_data["overtime"] = False

    return cleaned_data


def check_dnf(game: dict):
    for club in game["clubs"]:
        if (
            game["clubs"][club]["winner by DNF"] != "0"
            or game["clubs"][club]["winner by goalie DNF"] != "0"
        ):
            return True
    return False


def check_no_game(game: dict):
    zero = []
    for club in game["clubs"]:
        if str(game["clubs"][club]["shots"]) == "0":
            zero.append(True)
        else:
            zero.append(False)
    if all(zero):
        return True
    return False


def setup_messages(game, history, vs_matches):
    model = data_service.convert_match(game)
    our_team = game["clubs"][CLUB_ID]["details"]["name"]
    cleaned_game = chatify_data(game)
    cleaned_game["previous_games"] = history if history else {}
    formatted_game = format_game_data(cleaned_game)

    # Get matchup context if we have history
    matchup_context = ""
    if vs_matches:
        from ilobot.analysis.team_matchup import get_matchup_context

        context = get_matchup_context(
            model, [data_service.convert_match(h) for h in vs_matches]
        )
        matchup_context = "\n".join(context.values())

    now = datetime.date.today().strftime("%d %B")

    # Randomized style directives to ensure varied tone/structure each call
    style_cards = [
        "Kirjoita kuin krapulainen GM lehdistötilaisuudessa. Aloita napakalla otsikolla ja jatka kahdella lyhyellä kappaleella.",
        "Kirjoita kuin Mertaranta selostaisi jälkilähetyksessä. Yksi huudahdus sallittu. Vältä kliseitä.",
        "Kirjoita kuin lakoninen valmentaja-kehäraakki. Kuiva, pureva huumori, mutta pisteliäät tilasto-iskut.",
        "Kirjoita draamana: alku (syy), käänne (hetki), loppu (tuomio). Pidä kaikki suomeksi ja jääkiekkoslangilla.",
        "Kirjoita kuin fanin katkera rakkauskirje joukkueelle. Ironiaa, mutta rehelliset tilastot tukena.",
        "Kirjoita kuin kapteenin puhe bussissa. Ei siirappia, vain kova totuus ja yksi toivoa antava havainto.",
        "Kirjoita kuin radiostudioon soitettu ärsyyntynyt katsomokommentti – kuiva punchline loppuun.",
    ]
    chosen_style = random.choice(style_cards)

    messages = [
        {
            "role": "system",
            "content": f"""
Sinä olet {our_team}-seuran humalainen, sarkastinen suomalainen GM. Tehtäväsi on tuottaa viihdyttävä ja vaihteleva otteluraportti joka kerta:
- Käytä vain suomen kieltä ja jääkiekkoslangia.
- Sävytä tarina tilastoilla: roastaa kovalla kädellä, kehu vain jos on pakko.
- Raivoa erityisesti, jos hävitään alemmalle divarille.
- Vaihtele kerrontaa joka kerta: rakenne, sävy, vertauskuvat ja iskulauseet.
- Vältä toistuvia aloituslauseita ja fraaseja; älä koskaan selitä ohjeitasi tai paljasta rooliasi.
- Pidä pituus alle 280 sanaa.
""",
        },
        {
            "role": "system",
            "content": f"Tyyli- ja rakennekortti: {chosen_style} Älä mainitse, että valitsit tyylin.",
        },
        {
            "role": "user",
            "content": f"""
Tee suomeksi alle 280 sanan ottelukertomus keskittyen joukkueeseen {our_team}. Muotoile vaihtelevasti, ei listoja ellei tyyli sitä pyydä.

1) Joukkueen peli-identiteetti vs. tämä ilta – odotuksiin nähden yllätykset ja notkahdukset.
2) Divariero ja putket – mainitse vain jos taidollinen kuilu on oikeasti merkittävä, käytä draaman polttoaineena.
3) Pelaajat – käytä täsmätilastoja: kuka kantoi, kuka suli, mikä yksittäinen hetki muutti pelin.
4) Jos DNF – kyseenalaista selkäranka, mutta pidä teksti hauskan piikikkäänä.

Vaatimukset: vältä kliseitä, vaihtele aloitus, käytä yhtä tuoretta kielikuvaa ja lopeta yhdellä nasevalla toteamuksella.
""",
        },
    ]

    # Add game data
    messages.append(
        {
            "role": "user",
            "content": "\n###\nGame Data:\n" + formatted_game + "\n\n",
        }
    )

    # Add matchup context if available
    if matchup_context:
        messages.append(
            {
                "role": "user",
                "content": "\n###\nMatchup Context:\n" + matchup_context + "\n\n",
            }
        )

    if model.clubs[CLUB_ID].get_match_type().value == MatchType.THREE_ON_THREE.value:
        # messages.append(
        #     {
        #         "role": "user",
        #         "content": f"Match was played as 3vs3, meaning each team had 3 skaters and a goalie on ice. This game mode doesn't have regular penalties, only penalty shots. ",
        #     }
        # )
        pass

    if random.randint(0, 7) == 0:
        messages.append(
            {
                "role": "user",
                "content": (
                    f"Mausta tekstiä kevyesti, jos ajankohta {now} osuu juhlaan tai merkittävään urheilutapahtumaan – korkeintaan kaksi viittausta, ei selittelyä."
                ),
            }
        )

    return messages


async def write_gpt_summary(game: dict, history=None, vs_matches=None):
    messages = setup_messages(game, history, vs_matches)
    try:
        client = AsyncOpenAI(
            api_key=OPEN_API,
        )

        model = GPT_MODEL
        # Randomize sampling params per call for higher output diversity
        temperature = round(random.uniform(1.3, 1.9), 2)
        top_p = round(random.uniform(0.85, 0.98), 2)
        frequency_penalty = round(random.uniform(0.9, 1.6), 2)
        presence_penalty = round(random.uniform(1.0, 1.5), 2)

        chat_completion = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
        )
    except OpenAIError:
        logger.exception("OPENAI error")
        return None
    return chat_completion.choices[0].message.content
