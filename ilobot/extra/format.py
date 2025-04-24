import json

# Example analysis data
"""
**Current Win Streak for us: 11**

### Ilo Pisara (Away | Win)
**Season Stats**
- record: 714-111-24 (84.1% wins, 85.5% points)
- scoring: 5.49 GF/2.39 GA per game (+3.09 diff)
- totals: 4657 GF/2032 GA (+2625 diff)
- division: 1 | rank: 0 | streak: N/A | last10: N/A
**Game Stats**
- score: 5-4 | shots: 14 | hits: 3
- Players:
    - Teppo Winnipeg (Offensive Defenseman)
        - Position: Defensemen
        - Ratings: Off 80.00, Def 60.00, Team 60.00
        - Points: 3 (Goals: 0, Assists: 3)
        - Shooting: 1/3 on net, 0.00% scoring
        - Takeaway/Giveaway Ratio: 0.5
        - Impact Stats: Blocks 2, Hits 1, Interceptions 3, Takeaways 3, Giveaways 6
    - Idän Jätti (Dangler)
        - Position: Leftwing
        - Ratings: Off 90.00, Def 60.00, Team 50.00
        - Points: 4 (Goals: 3, Assists: 1)
        - Shooting: 7/7 on net, 42.86% scoring
        - Takeaway/Giveaway Ratio: 0.25
        - Impact Stats: Blocks 0, Hits 0, Interceptions 2, Takeaways 1, Giveaways 4
    - Jani Saari (Grinder)
        - Position: Center
        - Ratings: Off 100.00, Def 55.00, Team 80.00
        - Points: 5 (Goals: 2, Assists: 3)
        - Shooting: 3/4 on net, 66.67% scoring
        - Takeaway/Giveaway Ratio: 0.36
        - Impact Stats: Blocks 1, Hits 2, Interceptions 4, Takeaways 4, Giveaways 11
        - Faceoffs: Won 15, Lost 6 (Win Rate: 71.43%)

### Gotham Knights (Home | Loss)
**Season Stats**
- record: 262-51-7 (81.9% wins, 83.0% points)
- scoring: 4.98 GF/2.51 GA per game (+2.47 diff)
- totals: 1594 GF/803 GA (+791 diff)
- division: 1 | rank: 0 | streak: N/A | last10: N/A
**Game Stats**
- score: 4-5 | shots: 18 | hits: 7
- Players:
    -  Hapettaja (Sniper)
        - Position: Leftwing
        - Ratings: Off 95.00, Def 70.00, Team 60.00
        - Points: 4 (Goals: 1, Assists: 3)
        - Shooting: 7/9 on net, 14.29% scoring
        - Takeaway/Giveaway Ratio: 0.5
        - Impact Stats: Blocks 1, Hits 1, Interceptions 3, Takeaways 3, Giveaways 6
    - Luca Bauer (Hybrid)
        - Position: Goalie
        - Saves: 9 out of 14 shots
        - Save Percentage: 0.64%
        - Goals Against: 5
        - Shutout Periods: 2
        - Breakaway Saves: 1/2 (Save Percentage: 0.50%)
        - Penalty Shots Saved: 0/0 (Save Percentage: 0.00%)
    -  Alistaja (Offensive Defenseman)
        - Position: Defensemen
        - Ratings: Off 95.00, Def 30.00, Team 70.00
        - Points: 2 (Goals: 2, Assists: 0)
        - Shooting: 5/7 on net, 40.00% scoring
        - Takeaway/Giveaway Ratio: 0.5
        - Impact Stats: Blocks 1, Hits 3, Interceptions 3, Takeaways 3, Giveaways 6
    - A Konna (Sniper)
        - Position: Center
        - Ratings: Off 100.00, Def 75.00, Team 50.00
        - Points: 4 (Goals: 1, Assists: 3)
        - Shooting: 5/7 on net, 20.00% scoring
        - Takeaway/Giveaway Ratio: 1.0
        - Impact Stats: Blocks 1, Hits 3, Interceptions 7, Takeaways 4, Giveaways 4
        - Faceoffs: Won 6, Lost 15 (Win Rate: 28.57%)
"""


# Function to format skater details
def format_skater(player_data):
    name = (
        player_data["playername"][1:]
        if player_data["playername"].startswith("-")
        else player_data["playername"]
    )
    # Calculate efficiency metrics
    takeaway_ratio = round(
        float(player_data.get("skater takeaways", 0))
        / max(float(player_data.get("skater giveaways", 1)), 1),
        2,
    )

    if player_data["position"].capitalize() == "Center":
        faceoffs = f"\n        - Faceoffs: Won {player_data.get('skater faceoff won', 0)}, Lost {player_data.get('skater faceoffs lost', 0)} "
        faceoffs += (
            f"(Win Rate: {player_data.get('skater faceoffs percentage', 'N/A')}%)"
        )
    else:
        faceoffs = ""

    return (
        f"\n"
        f"    - {name} ({player_data['class']})\n"
        f"        - Position: {player_data['position'].capitalize()}\n"
        f"        - Ratings: Off {player_data['ratingOffense']}, Def {player_data['ratingDefense']}, Team {player_data['ratingTeamplay']}\n"
        f"        - Points: {player_data['skater points']} (Goals: {player_data.get('skater goals', 0)}, Assists: {player_data.get('skater assists', 0)})\n"
        f"        - Shooting: {player_data['skater shots']}/{player_data['skater shot attempts']} on net, {player_data['skater shots percentage']}% scoring\n"
        f"        - Takeaway/Giveaway Ratio: {takeaway_ratio}\n"
        f"        - Impact Stats: Blocks {player_data.get('skater blocked shots', 0)}, Hits {player_data.get('skater hits', 0)}, "
        f"Interceptions {player_data.get('skater interceptions', 0)}, Takeaways {player_data.get('skater takeaways', 0)}, Giveaways {player_data.get('skater giveaways', 0)}"
        f"{faceoffs}"
    )


# Function to format goalie details
def format_goalie(player_data):
    name = (
        player_data["playername"][1:]
        if player_data["playername"].startswith("-")
        else player_data["playername"]
    )
    return (
        f"\n"
        f"    - {name} ({player_data['class']})\n"
        f"        - Position: Goalie\n"
        f"        - Saves: {player_data['goalie saves']} out of {player_data['goalie shots']} shots\n"
        f"        - Save Percentage: {player_data['goalie save percentage']}%\n"
        f"        - Goals Against: {player_data['goalie goals against']}\n"
        f"        - Shutout Periods: {player_data.get('goalie shutout periods', 0)}\n"
        f"        - Breakaway Saves: {player_data['goalie breakaway saves']}/{player_data['goalie breakaway shots']}"
        f" (Save Percentage: {player_data['goalie breakaway saves percentage']}%)\n"
        f"        - Penalty Shots Saved: {player_data['goalie penalty shot saves']}/{player_data['goalie penalty shots']}"
        f" (Save Percentage: {player_data['goalie penalty shot percentage']}%)"
    )


def format_player(player_data):
    if player_data["position"].lower() == "goalie":
        return format_goalie(player_data)
    else:
        return format_skater(player_data)


# Function to format the club details
def format_club(club_name, club_data, overtime):
    goals = club_data["goals"]
    goalsAgainst = club_data["goalsAgainst"]
    win = "Win" if int(goals) > int(goalsAgainst) else "Loss"
    if overtime:
        win += " (OT)"
    formatted_club = f"### {club_name} ({'Home' if club_data['teamSide'] == '0' else 'Away'} | {win})\n"

    # Add team analysis if available
    if "team_analysis" in club_data:
        formatted_club += "**Season Stats**\n"
        for stat in club_data["team_analysis"]:
            formatted_club += f"- {stat}\n"

    if not club_data["no_game"]:
        formatted_club += (
            "**Game Stats**\n"
            f"- score: {goals}-{goalsAgainst} | shots: {club_data['shots']} | hits: {club_data['hits']}\n"
        )

    if club_data["winner by DNF"] != "0" or club_data["winner by goalie DNF"] != "0":
        formatted_club += "- won by DNF\n"

    if club_data["players"]:
        if not club_data["no_game"]:
            formatted_club += "- Players:"
            for player_name, player_data in club_data["players"].items():
                formatted_club += format_player(player_data)
    else:
        formatted_club += "- Players: (No player data available)\n"

    formatted_club += "\n\n"
    return formatted_club


# Function to format the previous games
def format_previous_games(games):
    formatted_games = "\n# Previous Games\n"
    for game in games:
        formatted_games += (
            f"- {game['date_time']}: {game['game_outcome']} - "
            f"{'Win' if game['win'] else 'Loss'}\n"
        )
    return formatted_games


# Function to calculate win streak
def calculate_win_streak(previous_games):
    if not previous_games:
        return (0, "")
    streak = 0
    first_game = previous_games[0]["win"]
    for game in previous_games:
        if game["win"] == first_game:
            streak += 1
        else:
            break
    streak_type = "win streak" if first_game else "losing streak"
    return (streak, streak_type)


# Main function to format the JSON data
def format_game_data(json_data, title="Match"):
    formatted_output = f"# {title}\n\n"

    # Calculate and add streak
    if "previous_games" in json_data:
        streak_count, streak_type = calculate_win_streak(json_data["previous_games"])
        if streak_count > 0:
            formatted_output += f"**Current {streak_type} for us: {streak_count}**\n\n"

    # Format clubs
    overtime = json_data["overtime"]
    for club_name, club_data in json_data["clubs"].items():
        formatted_output += format_club(club_name, club_data, overtime)

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
