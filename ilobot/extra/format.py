import json


# Function to format skater details
def format_skater(player_data):
    return (
        f"  - {player_data['playername']} ({player_data['class']})\n"
        f"    - Position: {player_data['position'].capitalize()}\n"
        f"    - Offense Rating: {player_data['ratingOffense']}\n"
        f"    - Defense Rating: {player_data['ratingDefense']}\n"
        f"    - Teamplay Rating: {player_data['ratingTeamplay']}\n"
        f"    - Points: {player_data['skater points']} (Goals: {player_data.get('skater goals', 0)}, Assists: {player_data.get('skater assists', 0)})\n"
        f"    - Shots on Net: {player_data['skater shots']}/{player_data['skater shot attempts']} ({player_data['skater shots on net percentage']}%)\n"
        f"    - Passes: {player_data['skater passes']} (Pass Percentage: {player_data['skater pass percentage']}%)\n"
        f"    - Other stats: Blocked Shots: {player_data.get('skater blocked shots', 0)}, Hits: {player_data.get('skater hits', 0)}, "
        f"Interceptions: {player_data.get('skater interceptions', 0)}, Takeaways: {player_data.get('skater takeaways', 0)}, "
        f"Faceoffs Won: {player_data.get('skater faceoff won', 0)}, Faceoffs Lost: {player_data.get('skater faceoffs lost', 0)}, "
        f"Faceoff Percentage: {player_data.get('skater faceoffs percentage', 'N/A')}%\n"
    )


# Function to format goalie details
def format_goalie(player_data):
    return (
        f"  - {player_data['playername']} ({player_data['class']})\n"
        f"    - Position: Goalie\n"
        f"    - Saves: {player_data['goalie saves']} out of {player_data['goalie shots']} shots\n"
        f"    - Save Percentage: {player_data['goalie save percentage']}%\n"
        f"    - Goals Against: {player_data['goalie goals against']}\n"
        f"    - Shutout Periods: {player_data.get('goalie shutout periods', 0)}\n"
        f"    - Breakaway Saves: {player_data['goalie breakaway saves']}/{player_data['goalie breakaway shots']} "
        f"(Save Percentage: {player_data['goalie breakaway saves percentage']}%)\n"
        f"    - Penalty Shots Saved: {player_data['goalie penalty shot saves']}/{player_data['goalie penalty shots']} "
        f"(Save Percentage: {player_data['goalie penalty shot percentage']}%)\n"
    )


def format_player(player_data):
    if player_data["position"].lower() == "goalie":
        return format_goalie(player_data)
    else:
        return format_skater(player_data)


# Function to format the club details
def format_club(club_name, club_data):
    formatted_club = (
        f"#### {club_name}\n"
        f"- Result: {'Win' if club_data['result'] == '1' else 'Loss'} ({club_data['scoreString']})\n"
        f"- Score: {club_data['goals']} (Goals) - {club_data['goalsAgainst']} (Goals Against)\n"
        f"- Shots: {club_data['shots']}\n"
        f"- Team Side: {'Home' if club_data['teamSide'] == '0' else 'Away'}\n"
        f"- Winner by DNF: {'Yes' if club_data['winner by DNF'] != '0' else 'No'}\n"
        f"- Winner by Goalie DNF: {'Yes' if club_data['winner by goalie DNF'] != '0' else 'No'}\n"
    )

    if club_data["players"]:
        formatted_club += "- Players:\n"
        for player_name, player_data in club_data["players"].items():
            formatted_club += format_player(player_data)
    else:
        formatted_club += "- Players: (No player data available)\n"

    return formatted_club


# Function to format the previous games
def format_previous_games(games):
    formatted_games = "\n### Previous Games:\n"
    for game in games:
        formatted_games += (
            f"{game['date_time']}: {game['game_outcome']} - "
            f"{'Win' if game['win'] else 'Loss'}\n"
        )
    return formatted_games


# Main function to format the JSON data
def format_game_data(json_data):
    formatted_output = "### Clubs:\n"

    # Format clubs data
    for club_name, club_data in json_data["clubs"].items():
        formatted_output += format_club(club_name, club_data)

    # Format previous games data
    if "previous_games" in json_data:
        formatted_output += format_previous_games(json_data["previous_games"])

    return formatted_output


# Sample JSON input
json_input = """
{
    "clubs": {
        "Ilo Pisara": {
            "result": "1",
            "score": "5",
            "scoreString": "5 - 4",
            "shots": "14",
            "teamSide": "1",
            "winner by DNF": "0",
            "winner by goalie DNF": "0",
            "goals": "5",
            "goalsAgainst": "4",
            "players": {
                "Teppo Winnipeg": {
                    "class": "Offensive Defenseman",
                    "isGuest": "0",
                    "position": "defenseMen",
                    "ratingDefense": "60.00",
                    "ratingOffense": "80.00",
                    "ratingTeamplay": "60.00",
                    "skater assists": "3",
                    "skater blocked shots": "2",
                    "skater deflections": "0",
                    "skater goals": "0",
                    "skater game winning goals": "0",
                    "skater hits": "1",
                    "skater interceptions": "3",
                    "skater passes": "13",
                    "skater pass percentage": "65.00",
                    "skater penalty minutes": "0",
                    "skater clearzone": "0",
                    "skater plus minus": "1",
                    "skater possession": "263",
                    "skater saucer passes": "0",
                    "skater shorthanded goals": "0",
                    "skater shot attempts": "3",
                    "skater shots on net percentage": "33.33",
                    "skater shots percentage": "0.00",
                    "skater shots": "1",
                    "skater takeaways": "3",
                    "time on ice": "60",
                    "toiseconds": "3600",
                    "playername": "Teppo Winnipeg",
                    "clientPlatform": "ps5",
                    "skater points": 3
                },
                "Id\u00e4n J\u00e4tti": {
                    "class": "Dangler",
                    "isGuest": "0",
                    "position": "leftWing",
                    "ratingDefense": "60.00",
                    "ratingOffense": "90.00",
                    "ratingTeamplay": "50.00",
                    "skater assists": "1",
                    "skater blocked shots": "0",
                    "skater deflections": "0",
                    "skater goals": "3",
                    "skater game winning goals": "0",
                    "skater hits": "0",
                    "skater interceptions": "2",
                    "skater passes": "9",
                    "skater pass percentage": "75.00",
                    "skater penalty minutes": "0",
                    "skater clearzone": "0",
                    "skater plus minus": "1",
                    "skater possession": "413",
                    "skater saucer passes": "0",
                    "skater shorthanded goals": "0",
                    "skater shot attempts": "7",
                    "skater shots on net percentage": "100.00",
                    "skater shots percentage": "42.86",
                    "skater shots": "7",
                    "skater takeaways": "1",
                    "time on ice": "60",
                    "toiseconds": "3600",
                    "playername": "Id\u00e4n J\u00e4tti",
                    "clientPlatform": "ps5",
                    "skater points": 4
                },
                "Jani Saari": {
                    "class": "Grinder",
                    "isGuest": "0",
                    "position": "center",
                    "ratingDefense": "55.00",
                    "ratingOffense": "100.00",
                    "ratingTeamplay": "80.00",
                    "skater assists": "3",
                    "skater blocked shots": "1",
                    "skater deflections": "0",
                    "skater faceoffs lost": "6",
                    "skater faceoffs percentage": "71.43",
                    "skater faceoff won": "15",
                    "skater giveaways": "11",
                    "skater goals": "2",
                    "skater game winning goals": "1",
                    "skater hits": "2",
                    "skater interceptions": "4",
                    "skater passes": "12",
                    "skater pass percentage": "54.55",
                    "skater penalty minutes": "0",
                    "skater clearzone": "0",
                    "skater plus minus": "1",
                    "skater possession": "544",
                    "skater saucer passes": "0",
                    "skater shorthanded goals": "0",
                    "skater shot attempts": "4",
                    "skater shots on net percentage": "75.00",
                    "skater shots percentage": "66.67",
                    "skater shots": "3",
                    "skater takeaways": "4",
                    "time on ice": "60",
                    "toiseconds": "3600",
                    "playername": "Jani Saari",
                    "clientPlatform": "ps5",
                    "skater points": 5
                }
            },
            "clubId": "1205"
        },
        "Gotham Knights": {
            "result": "2",
            "score": "4",
            "scoreString": "4 - 5",
            "shots": "18",
            "teamSide": "0",
            "winner by DNF": "0",
            "winner by goalie DNF": "0",
            "goals": "4",
            "goalsAgainst": "5",
            "players": {
                "Harri Hapettaja": {
                    "class": "Sniper",
                    "isGuest": "1",
                    "position": "leftWing",
                    "ratingDefense": "70.00",
                    "ratingOffense": "95.00",
                    "ratingTeamplay": "60.00",
                    "skater assists": "3",
                    "skater blocked shots": "1",
                    "skater deflections": "0",
                    "skater goals": "1",
                    "skater game winning goals": "0",
                    "skater hits": "1",
                    "skater interceptions": "3",
                    "skater passes": "15",
                    "skater pass percentage": "78.95",
                    "skater penalty minutes": "0",
                    "skater clearzone": "0",
                    "skater plus minus": "-1",
                    "skater possession": "518",
                    "skater saucer passes": "1",
                    "skater shorthanded goals": "0",
                    "skater shot attempts": "9",
                    "skater shots on net percentage": "77.78",
                    "skater shots percentage": "14.29",
                    "skater shots": "7",
                    "skater takeaways": "3",
                    "time on ice": "60",
                    "toiseconds": "3600",
                    "playername": "Harri Hapettaja",
                    "clientPlatform": "ps5",
                    "skater points": 4
                },
                "Luca Bauer": {
                    "class": "Hybrid",
                    "goalie breakaway saves percentage": "0.50",
                    "goalie breakaway saves": "1",
                    "goalie breakaway shots": "2",
                    "goalie dsaves": "0",
                    "goalie goals against": "5",
                    "goalie goals against average": "5.00",
                    "goalie penalty shot percentage": "0.00",
                    "goalie penalty shot saves": "0",
                    "goalie penalty shots": "0",
                    "goalie pkclearzone": "0",
                    "goalie poke checks": "0",
                    "goalie save percentage": "0.64",
                    "goalie saves": "9",
                    "goalie shots": "14",
                    "goalie shutout periods": "2",
                    "isGuest": "0",
                    "position": "goalie",
                    "ratingDefense": "70.00",
                    "ratingOffense": "40.00",
                    "ratingTeamplay": "55.00",
                    "time on ice": "60",
                    "toiseconds": "3599",
                    "playername": "Luca Bauer",
                    "clientPlatform": "ps5"
                },
                "Alvari Alistaja": {
                    "class": "Offensive Defenseman",
                    "isGuest": "1",
                    "position": "defenseMen",
                    "ratingDefense": "30.00",
                    "ratingOffense": "95.00",
                    "ratingTeamplay": "70.00",
                    "skater assists": "0",
                    "skater blocked shots": "1",
                    "skater deflections": "1",
                    "skater goals": "2",
                    "skater game winning goals": "0",
                    "skater hits": "3",
                    "skater interceptions": "3",
                    "skater passes": "12",
                    "skater pass percentage": "80.00",
                    "skater penalty minutes": "0",
                    "skater clearzone": "0",
                    "skater plus minus": "-1",
                    "skater possession": "308",
                    "skater saucer passes": "0",
                    "skater shorthanded goals": "0",
                    "skater shot attempts": "7",
                    "skater shots on net percentage": "71.43",
                    "skater shots percentage": "40.00",
                    "skater shots": "5",
                    "skater takeaways": "3",
                    "time on ice": "60",
                    "toiseconds": "3600",
                    "playername": "Alvari Alistaja",
                    "clientPlatform": "ps5",
                    "skater points": 2
                },
                "Joona L\u00f6ytynoja": {
                    "class": "Sniper",
                    "isGuest": "1",
                    "position": "center",
                    "ratingDefense": "75.00",
                    "ratingOffense": "100.00",
                    "ratingTeamplay": "50.00",
                    "skater assists": "3",
                    "skater blocked shots": "1",
                    "skater deflections": "0",
                    "skater faceoffs lost": "15",
                    "skater faceoffs percentage": "28.57",
                    "skater faceoff won": "6",
                    "skater goals": "1",
                    "skater game winning goals": "0",
                    "skater hits": "3",
                    "skater interceptions": "7",
                    "skater passes": "12",
                    "skater pass percentage": "100.00",
                    "skater penalty minutes": "2",
                    "skater clearzone": "0",
                    "skater plus minus": "-1",
                    "skater possession": "226",
                    "skater saucer passes": "1",
                    "skater shorthanded goals": "0",
                    "skater shot attempts": "7",
                    "skater shots on net percentage": "71.43",
                    "skater shots percentage": "20.00",
                    "skater shots": "5",
                    "skater takeaways": "4",
                    "time on ice": "60",
                    "toiseconds": "3600",
                    "playername": "Joona L\u00f6ytynoja",
                    "clientPlatform": "ps5",
                    "skater points": 4
                }
            },
            "clubId": "1815"
        }
    },
    "win": true,
    "previous_games": [
        {
            "date_time": "11.10. 00:18",
            "game_outcome": "Ilo Pisara vs Gotham Knights 5 - 4",
            "win": true,
            "gm_recap_abstract": ""
        },
        {
            "date_time": "10.10. 23:53",
            "game_outcome": "Ilo Pisara vs RAGEQUIT 4 - 0",
            "win": true,
            "gm_recap_abstract": ""
        },
        {
            "date_time": "10.10. 23:32",
            "game_outcome": "Ilo Pisara vs FENIX 6 - 3",
            "win": true,
            "gm_recap_abstract": ""
        },
        {
            "date_time": "10.10. 23:09",
            "game_outcome": "Ilo Pisara vs Ice Wolves eSports 6 - 2",
            "win": true,
            "gm_recap_abstract": ""
        }
    ]
}
"""
if __name__ == "__main__":

    # Parse JSON input
    game_data = json.loads(json_input)

    # Print formatted output
    print(format_game_data(game_data))
