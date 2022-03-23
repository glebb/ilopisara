import jsonmap
from datetime import datetime
import pytz
import os
from dotenv import load_dotenv
load_dotenv('../.env')
CLUB_ID = os.getenv('CLUB_ID')

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
    opponentName = match['clubs'][opponentId]['details']['name'] if match['clubs'][opponentId]['details'] != None else "???"
    score_teams = match['clubs'][os.getenv('CLUB_ID')]['details']['name'] + ' - ' + opponentName
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
    for _, p in sorted(match['players'][os.getenv('CLUB_ID')].items(), key=lambda p: int(p[1]['skgoals']) + int(p[1]['skassists']), reverse=True):
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
    reply = f"Top {stats_filter}\n"
    try:
        for member in sorted(members, key=lambda m: float(m[key]), reverse=True):
            reply += member['name'] + ' ' + member[key] + "\n"
    except (TypeError, ValueError):
        for member in sorted(members, key=lambda m: m[key], reverse=True):
            reply += member['name'] + ' ' + member[key] + "\n"
    except KeyError:
        reply = ""
    if reply:
        return reply
    
def game_record(matches, stats_filter):
    key = jsonmap.get_key(stats_filter)
    ref_matches = []
    for match in matches:
        for playerid, data in match['players'][CLUB_ID].items():
            if key == 'points' or key == 'skpoints':
                data[key] = str(int(float(data['skgoals']) + float(data['skassists'])))
                match['players'][CLUB_ID][playerid] = data
            try:
                if (not ref_matches and key in data) or float(data[key]) > float(ref_matches[0][1]['players'][CLUB_ID][ref_matches[0][0]][key]):
                    ref_matches.clear()
                    ref_matches.append([playerid, match, key])
                elif float(data[key]) == float(ref_matches[0][1]['players'][CLUB_ID][ref_matches[0][0]][key]):
                    ref_matches.append([playerid, match, key])
            except (TypeError, ValueError):
                pass
            except KeyError:
                pass
           
    if ref_matches:
        return ref_matches

def team_record(team):
    if not team:
        return None
    key = list(team.keys())[0]
    reply = ""
    if key:
        reply += "Team: " + team[key]['name'] + "\n"
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
    f = open('tests/members.json',)
    members = json.load(f)
    f.close()

    f = open('tests/matches.json',)
    matches = json.load(f)
    f.close()

    f = open('tests/team.json',)
    team = json.load(f)
    f.close()


    #print(format_stats(members['members'][0], None))
    #print(format_result(matches[0]))
    #print(match_details(matches[1]))
    #print(top_stats(members['members'], 'skater goals'))
    #print(team_record(team))
    print(len(game_record(matches, "xca dsfgsd gfsd")))