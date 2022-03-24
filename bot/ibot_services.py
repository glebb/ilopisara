import jsonmap
import interactions
from data import api


def get_stats_choice_chunks():
    all_stats_as_choices = []
    for key, value in jsonmap.names.items():
        choice = interactions.Choice(
            name=key,
            value=key,
        )
        all_stats_as_choices.append(choice)

    n = 24
    stat_choice_chunks = [
        all_stats_as_choices[i : i + n] for i in range(0, len(all_stats_as_choices), n)
    ]
    return stat_choice_chunks

def get_match_stats_choice_chucnks():
    all_stats_as_choices = []
    for stat in jsonmap.match:
        choice = interactions.Choice(
            name=stat,
            value=stat,
        )
        all_stats_as_choices.append(choice)

    n = 24
    stat_choice_chunks = [
        all_stats_as_choices[i : i + n] for i in range(0, len(all_stats_as_choices), n)
    ]
    return stat_choice_chunks
    

def get_member_choices():
    members = api.get_members()["members"]
    all_names = []
    for member in members:
        choice = interactions.Choice(
            name=member['name'],
            value=member['name'],
        )
        all_names.append(choice)
    return all_names
