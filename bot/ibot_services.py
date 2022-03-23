import jsonmap
import interactions

def get_stats_choice_chunks():
    all_stats_as_choices = []
    for key, value in jsonmap.names.items():
        choice = interactions.Choice(
        name=key,
        value=key,
    )    
        all_stats_as_choices.append(choice)

    n=24
    stat_choice_chunks=[all_stats_as_choices[i:i + n] for i in range(0, len(all_stats_as_choices), n)]
    return stat_choice_chunks