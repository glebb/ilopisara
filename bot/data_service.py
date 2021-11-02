import jsonmap
from datetime import datetime
import pytz
from dotenv import load_dotenv
import os

def find(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return None

def format_result(match):
    ts = int(match['timestamp'])
    score_time = datetime.fromtimestamp(ts)
    score_time = score_time.astimezone(pytz.timezone('Europe/Helsinki')).strftime('%d.%m. %H:%M')
    opponentId = match['clubs'][os.getenv('CLUB_ID')]['opponentClubId']
    score_teams = match['clubs'][os.getenv('CLUB_ID')]['details']['name'] + ' - ' + match['clubs'][opponentId]['details']['name']
    score_result = match['clubs'][os.getenv('CLUB_ID')]['scoreString']
    score_string = score_time + ' ' + score_teams + ' ' + score_result + ' ' + ' // '+ match['matchId']
    return score_string

def format_stats(stats, stats_filter):
    message = ""
    for k, v in sorted(stats.items()):
        stat = None
        key = jsonmap.get_name(k)
        if stats_filter and key.startswith(stats_filter.lower()):
            stat = key + ': ' + v
        elif not stats_filter:
            if not key.startswith('skater') and not key.startswith('goalie') and not key.startswith('xfactor'):
                stat = key + ': ' + v
        if stat:
            message += stat + "\n"
    if message:
        return message

def match_details(match):
    players = ""
    for k, p in sorted(match['players'][os.getenv('CLUB_ID')].items(), key=lambda p: int(p[1]['skgoals']) + int(p[1]['skassists']), reverse=True):
        filler = 3 - len(p['position'])
        players += p['position'][0].upper() + ' ' + p['playername'] + ', '
        if p['position'] == 'goalie':
            players += 'save %:' + p['glsavepct'] + ', '
            players += 'saves:' + p['glsaves'] + ', '
            players += 'shots:' + p['glshots'] + "\n"
        else:
            players += p['skgoals'] + '+' + p['skassists'] + ', '
            players += 'shots:' + p['skshots'] + ', '
            players += 'hits:' + p['skhits'] + ', '
            players += 'blocked shots:' + p['skbs'] + ', '
            players += 'p/m:' + p['skplusmin'] + ', '
            players += 'penalties:' + p['skpim'] + "m\n"
    return players

def top_stats(members, stats_filter):
    key = jsonmap.get_key(stats_filter)
    reply = ""
    try:
        for member in sorted(members, key=lambda m: float(m[key]), reverse=True):
            reply += member['name'] + ' ' + member[key] + "\n"
    except (TypeError, ValueError):
        for member in sorted(members, key=lambda m: m[key], reverse=True):
            reply += member['name'] + ' ' + member[key] + "\n"
    except KeyError:
        pass
    if reply:
        return reply

def team_record(team):
    if not team:
        return None
    key = list(team.keys())[0]
    reply = ""
    if key:
        reply += team[key]['name'] + "\n"
        reply += "points: " + team[key]['rankingPoints'] + "\n"
        reply += "record: " + team[key]['record'] + "\n"
        reply += "current division: " + str(team[key]['currentDivision']) + "\n"
        games = int(team[key]['wins']) + int(team[key]['losses']) + int(team[key]['ties']) + int(team[key]['otl'])
        if games > 0:
            goals_per_game =  + int(team[key]['goals']) / games
            goals_against_per_game =  + int(team[key]['goalsAgainst']) / games
        else:
            goals_per_game = 0
            goals_against_per_game = 0
        reply += "goals per game: " + "{:.2f}".format(goals_per_game) + "\n"
        reply += "goals against per game: " + "{:.2f}".format(goals_against_per_game)
    if reply:
        return reply

if __name__ == '__main__':
    import json
    f = open('members.json',)
    members = json.load(f)
    f.close()

    f = open('matches.json',)
    matches = json.load(f)
    f.close()

    f = open('team.json',)
    team = json.load(f)
    f.close()


    print(format_stats(members['members'][0], None))
    print(format_result(matches[0]))
    print(match_details(matches[1]))
    print(top_stats(members['members'], 'skater goals'))
    print(team_record(team))