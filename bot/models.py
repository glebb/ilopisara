from dataclasses import dataclass
from typing import Dict

# pylint: disable=C0103


@dataclass
class Result:
    mark: str
    date_and_time: str
    score: str
    game_type: str
    match_id: str

    def __str__(self):
        return (
            self.mark
            + " "
            + self.date_and_time
            + " "
            + self.score
            + " "
            + self.game_type
            + " // "
            + self.match_id
        )

    def discord_print(self):
        return (
            self.mark
            + " **"
            + self.date_and_time
            + " "
            + self.score
            + "** "
            + self.game_type
            + " // "
            + self.match_id
        )


@dataclass
class MatchTimeAgo:
    number: int
    unit: str


@dataclass
class MatchClubAggregate:
    glbrksavepct: float
    glbrksaves: int
    glbrkshots: int
    gldsaves: int
    glga: int
    glgaa: float
    glpensavepct: float
    glpensaves: int
    glpenshots: int
    glpkclearzone: int
    glpokechecks: int
    glsavepct: float
    glsaves: int
    glshots: int
    glsoperiods: int
    isGuest: int
    memberString: int
    opponentClubId: int
    opponentScore: int
    player_dnf: int
    playerLevel: int
    pNhlOnlineGameType: int
    position: int
    posSorted: int
    rankpoints: int
    ranktierassetid: int
    ratingDefense: float
    ratingOffense: float
    ratingTeamplay: float
    removedReason: int
    result: int
    score: int
    scoreRaw: int
    scoreString: int
    skassists: int
    skbs: int
    skdeflections: int
    skfol: int
    skfopct: float
    skfow: int
    skgiveaways: int
    skgoals: int
    skgwg: int
    skhits: int
    skinterceptions: int
    skpassattempts: int
    skpasses: int
    skpasspct: float
    skpenaltiesdrawn: int
    skpim: int
    skpkclearzone: int
    skplusmin: int
    skpossession: int
    skppg: int
    sksaucerpasses: int
    skshg: int
    skshotattempts: int
    skshotonnetpct: float
    skshotpct: float
    skshots: int
    sktakeaways: int
    teamSide: int
    toi: int
    toiseconds: int


@dataclass
class MatchClubDetailCustomKit:
    crestAssetId: str
    isCustomTeam: str
    useBaseAsset: str


@dataclass
class MatchClubDetail:
    name: str
    clubId: int
    regionId: int
    teamId: int
    customKit: MatchClubDetailCustomKit


@dataclass
class MatchClubData:
    clubDivision: str
    cNhlOnlineGameType: str
    garaw: str
    gfraw: str
    losses: str
    memberString: str
    opponentClubId: str
    opponentScore: str
    opponentTeamArtAbbr: str
    passa: str
    passc: str
    ppg: str
    ppo: str
    result: str
    score: str
    scoreString: str
    shots: str
    teamArtAbbr: str
    teamSide: str
    toa: str
    winnerByDnf: str
    winnerByGoalieDnf: str
    details: MatchClubDetail
    goals: str
    goalsAgainst: str


@dataclass
class MatchPlayerData:
    glbrksavepct: str
    glbrksaves: str
    glbrkshots: str
    gldsaves: str
    glga: str
    glgaa: str
    glpensavepct: str
    glpensaves: str
    glpenshots: str
    glpkclearzone: str
    glpokechecks: str
    glsavepct: str
    glsaves: str
    glshots: str
    glsoperiods: str
    isGuest: str
    memberString: str
    opponentClubId: str
    opponentScore: str
    player_dnf: str
    playerLevel: str
    pNhlOnlineGameType: str
    position: str
    posSorted: str
    rankpoints: str
    ranktierassetid: str
    ratingDefense: str
    ratingOffense: str
    ratingTeamplay: str
    removedReason: str
    result: str
    score: str
    scoreRaw: str
    scoreString: str
    skassists: str
    skbs: str
    skdeflections: str
    skfol: str
    skfopct: str
    skfow: str
    skgiveaways: str
    skgoals: str
    skgwg: str
    skhits: str
    skinterceptions: str
    skpassattempts: str
    skpasses: str
    skpasspct: str
    skpenaltiesdrawn: str
    skpim: str
    skpkclearzone: str
    skplusmin: str
    skpossession: str
    skppg: str
    sksaucerpasses: str
    skshg: str
    skshotattempts: str
    skshotonnetpct: str
    skshotpct: str
    skshots: str
    sktakeaways: str
    teamSide: str
    toi: str
    toiseconds: str
    playername: str


@dataclass
class Match:
    matchId: str
    timestamp: int
    timeAgo: MatchTimeAgo
    clubs: Dict[str, MatchClubData]
    players: Dict[str, Dict[str, MatchPlayerData]]
    aggregate: Dict[str, MatchClubAggregate]
    win: bool
    gameType: str
