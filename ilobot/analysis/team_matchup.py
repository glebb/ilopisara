"""Team matchup analysis module for providing context about team performance and matchups."""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from ilobot.models import Match
from ilobot import config

@dataclass
class TeamStats:
    """Statistics for a team."""
    wins: int = 0
    losses: int = 0
    otl: int = 0  # overtime losses
    goals_for: int = 0
    goals_against: int = 0
    division: Optional[int] = None
    
    @property
    def total_games(self) -> int:
        """Total number of games played."""
        return self.wins + self.losses + self.otl
    
    @property
    def win_percentage(self) -> float:
        """Win percentage including OT losses."""
        if self.total_games == 0:
            return 0.0
        return (self.wins + (self.otl * 0.5)) / self.total_games
    
    @property
    def goals_per_game(self) -> float:
        """Average goals scored per game."""
        if self.total_games == 0:
            return 0.0
        return self.goals_for / self.total_games
    
    @property
    def goals_against_per_game(self) -> float:
        """Average goals against per game."""
        if self.total_games == 0:
            return 0.0
        return self.goals_against / self.total_games


def get_team_name_from_id(team_id: str, match: Match) -> str:
    """Get team name from team ID using the match data."""
    if str(team_id) in match.clubs and match.clubs[str(team_id)].details:
        return match.clubs[str(team_id)].details.name
    return None

def calculate_team_stats(matches: List[Match], team_id: str) -> TeamStats:
    """Calculate team statistics using the EA NHL API."""
    from ilobot.data import api
    from ilobot import config
    
    # First get the team name from the match data
    team_name = None
    for match in matches:
        team_name = get_team_name_from_id(team_id, match)
        if team_name:
            break
    
    if not team_name:
        # If we can't find the team name, fall back to match-based stats
        return calculate_team_stats_from_matches(matches, team_id)
    
    # Get team record from API
    team_data = api.get_team_record(team_name, config.PLATFORM)
    if not team_data:
        # If API call fails, fall back to match-based stats
        return calculate_team_stats_from_matches(matches, team_id)
    
    stats = TeamStats()
    key = list(team_data.keys())[0]  # Team data is stored with club ID as key
    
    # Parse record string (format: "W-L-OTL")
    record = list(map(int, team_data[key]["record"].split("-")))
    stats.wins = record[0]
    stats.losses = record[1]
    stats.otl = record[2]
    
    # Get goals data
    stats.goals_for = int(team_data[key]["goals"])
    stats.goals_against = int(team_data[key]["goalsAgainst"])
    
    # Get division
    stats.division = int(team_data[key]["currentDivision"])
    
    return stats

def calculate_team_stats_from_matches(matches: List[Match], team_id: str) -> TeamStats:
    """Calculate team statistics from match history (fallback method)."""
    stats = TeamStats()
    
    for match in matches:
        if str(team_id) not in match.clubs:
            continue
            
        team_data = match.clubs[str(team_id)]
        opponent_id = team_data.opponentClubId
        
        # Update goals
        stats.goals_for += int(match.clubs[str(team_id)].goals)
        stats.goals_against += int(match.clubs[str(opponent_id)].goals)
        
        # Update division if not set
        if stats.division is None and team_data.clubDivision:
            stats.division = int(team_data.clubDivision)
        
        # Update win/loss record
        if team_data.result == "1":  # Win
            stats.wins += 1
        elif team_data.result == "2":  # Loss
            stats.losses += 1
        elif team_data.result == "3":  # OT Loss
            stats.otl += 1
            
    return stats


def analyze_head_to_head(matches: List[Match], our_team_id: str, opponent_id: str) -> Tuple[TeamStats, TeamStats]:
    """Analyze head-to-head matchups between two teams."""
    h2h_matches = [
        match for match in matches
        if str(opponent_id) in match.clubs and str(our_team_id) in match.clubs
    ]
    
    our_stats = calculate_team_stats(h2h_matches, our_team_id)
    opponent_stats = calculate_team_stats(h2h_matches, opponent_id)
    
    return our_stats, opponent_stats


def analyze_win_percentage_difference(our_pct: float, opp_pct: float) -> str:
    """Analyze the difference in win percentages between teams."""
    diff = abs(our_pct - opp_pct)
    if diff < 0.1:  # Less than 10% difference
        return "Teams are very evenly matched based on win rates"
    elif diff < 0.2:  # 10-20% difference
        better_team = "We are" if our_pct > opp_pct else "Opponent is"
        return f"{better_team} slightly favored based on win rates"
    else:  # More than 20% difference
        better_team = "We are" if our_pct > opp_pct else "Opponent is"
        return f"{better_team} heavily favored based on win rates"

def get_matchup_context(current_match: Match, recent_matches: List[Match]) -> Dict[str, str]:
    """Get context about the matchup for the current game."""
    our_team_id = str(config.CLUB_ID)
    opponent_id = current_match.clubs[our_team_id].opponentClubId
    
    # Get overall stats for both teams
    our_overall_stats = calculate_team_stats(recent_matches, our_team_id)
    opponent_overall_stats = calculate_team_stats(recent_matches, opponent_id)
    
    # Get head-to-head stats
    our_h2h_stats, opponent_h2h_stats = analyze_head_to_head(recent_matches, our_team_id, opponent_id)
    
    # Analyze win percentages
    win_pct_analysis = analyze_win_percentage_difference(
        our_overall_stats.win_percentage,
        opponent_overall_stats.win_percentage
    )
    
    # Analyze the matchup
    context = {
        "matchup_history": f"Head-to-head record: {our_h2h_stats.wins}-{our_h2h_stats.losses}-{our_h2h_stats.otl}",
        "our_form": f"Our overall record: {our_overall_stats.win_percentage:.1%} win rate ({our_overall_stats.wins}-{our_overall_stats.losses}-{our_overall_stats.otl})",
        "opponent_form": f"Opponent overall record: {opponent_overall_stats.win_percentage:.1%} win rate ({opponent_overall_stats.wins}-{opponent_overall_stats.losses}-{opponent_overall_stats.otl})",
        "win_percentage_comparison": win_pct_analysis
    }
    
    # Add division context if available
    if our_overall_stats.division is not None and opponent_overall_stats.division is not None:
        div_diff = our_overall_stats.division - opponent_overall_stats.division
        if div_diff > 0:
            context["division_context"] = f"Opponent is {div_diff} division(s) higher than us"
        elif div_diff < 0:
            context["division_context"] = f"We are {abs(div_diff)} division(s) higher than opponent"
    
    # Add scoring trends
    our_gf = our_overall_stats.goals_per_game
    our_ga = our_overall_stats.goals_against_per_game
    opp_gf = opponent_overall_stats.goals_per_game
    opp_ga = opponent_overall_stats.goals_against_per_game
    
    # Calculate offensive and defensive comparisons
    scoring_diff = our_gf - opp_gf
    defense_diff = our_ga - opp_ga
    
    offense_analysis = (
        "We score more" if scoring_diff > 0.5
        else "Opponent scores more" if scoring_diff < -0.5
        else "Teams score similarly"
    )
    
    defense_analysis = (
        "We allow fewer goals" if defense_diff < -0.5
        else "Opponent allows fewer goals" if defense_diff > 0.5
        else "Teams defend similarly"
    )
    
    context["scoring_trends"] = (
        f"Our avg: {our_gf:.1f} GF, {our_ga:.1f} GA | "
        f"Opp avg: {opp_gf:.1f} GF, {opp_ga:.1f} GA"
    )
    
    context["style_comparison"] = f"Style comparison: {offense_analysis}. {defense_analysis}."
    
    return context
