from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional

# pylint: disable=C0103


@dataclass
class MatchType(Enum):
    SIX_ON_SIX = "6vs6"
    THREE_ON_THREE = "3vs3"


@dataclass
class Result:
    mark: str
    date_and_time: str
    score: str
    game_type: str
    match_id: str
    match_type: MatchType

    def __str__(self):
        return self.date_and_time + " | " + self.score

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
            + self.match_type.value
        )

    def as_dict(self):
        return {"date_time": self.date_and_time, "game_outcome": self.score}


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

    def get_match_type(self):
        return (
            MatchType.THREE_ON_THREE
            if int(self.cNhlOnlineGameType) >= 200
            else MatchType.SIX_ON_SIX
        )


@dataclass
class MatchPlayerData:
    clientPlatform: Optional[str]
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
    skpoints: int


@dataclass
class Opponent:
    name: str
    id: str


@dataclass
class Match:
    matchId: str
    timestamp: int
    timeAgo: MatchTimeAgo
    clubs: Dict[str, MatchClubData]
    players: Dict[str, Dict[str, MatchPlayerData]]
    aggregate: Dict[str, MatchClubAggregate]
    win: bool
    opponent: Opponent
    gameType: str


@dataclass
class Club:
    clubId: int
    name: str
    rank: int
    clubName: str
    seasons: int
    divGroupsWon: int
    leaguesWon: int
    divGroupsWon1: int
    divGroupsWon2: int
    divGroupsWon3: int
    divGroupsWon4: int
    cupsWon1: int
    cupsWon2: int
    cupsWon3: int
    cupsWon4: int
    cupsWon5: int
    cupsElim1: int
    cupsElim2: int
    cupsElim3: int
    cupsElim4: int
    cupsElim5: int
    promotions: int
    holds: int
    relegations: int
    rankingPoints: str
    curCompetition: int
    prevDivision: int
    prevGameDivision: int
    bestDivision: int
    bestPoints: str
    curSeasonMov: int
    recentResult0: int
    recentResult1: int
    recentResult2: int
    recentResult3: int
    recentResult4: int
    recentResult5: int
    recentResult6: int
    recentResult7: int
    recentResult8: int
    recentResult9: int
    recentOpponent0: int
    recentOpponent1: int
    recentOpponent2: int
    recentOpponent3: int
    recentOpponent4: int
    recentOpponent5: int
    recentOpponent6: int
    recentOpponent7: int
    recentOpponent8: int
    recentOpponent9: int
    recentScore0: str
    recentScore1: str
    recentScore2: str
    recentScore3: str
    recentScore4: str
    recentScore5: str
    recentScore6: str
    recentScore7: str
    recentScore8: str
    recentScore9: str
    wins: int
    losses: int
    ties: int
    otl: int
    prevSeasonWins: int
    prevSeasonLosses: int
    prevSeasonTies: int
    prevSeasonOtl: int
    goals: int
    goalsAgainst: int
    starLevel: int
    totalCupsWon: int
    cupsEntered: int
    cupWinPercent: int
    titlesWon: int
    prevGameWonTitle: int
    record: str
    clubfinalsplayed: int
    divsWon1: int
    divsWon2: int
    divsWon3: int
    divsWon4: int
    currentDivision: int
    clubInfo: MatchClubDetail


@dataclass
class MemberRecord:
    wins: str
    losses: str
    otl: str
    winnerByDnf: str
    record: str
    skwins: str
    sklosses: str
    skotl: str
    skwinnerByDnf: str
    skgoals: str
    skassists: str
    skpoints: str
    skpointspg: str
    skgwg: str
    skplusmin: str
    sktoi: str
    skpim: str
    skppg: str
    skshg: str
    skpenaltyshotgoals: str
    skpenaltyattempts: str
    skpenaltyshotpct: str
    skoffsides: str
    skoffsidespg: str
    skfights: str
    skfightswon: str
    skfo: str
    skfow: str
    skfol: str
    skfop: str
    skhits: str
    skhitspg: str
    skbs: str
    skshots: str
    skshotpct: str
    skshotspg: str
    skshotattempts: str
    skshotonnetpct: str
    skpasses: str
    skpassattempts: str
    skpasspct: str
    sksaucerpasses: str
    skdekes: str
    skdekesmade: str
    skgiveaways: str
    sktakeaways: str
    skinterceptions: str
    skscrnchances: str
    skscrngoals: str
    skbrkgoals: str
    skbreakaways: str
    skbreakawaypct: str
    skgc: str
    skgcFC: str
    skhattricks: str
    skprevgoals: str
    skprevassists: str
    skpossession: str
    skdeflections: str
    skpkclearzone: str
    skpenaltiesdrawn: str
    glwins: str
    gllosses: str
    glotl: str
    glwinnerByDnf: str
    glshots: str
    glsaves: str
    glsavepct: str
    gltoi: str
    glga: str
    glgaa: str
    glso: str
    glsoperiods: str
    gldsaves: str
    glbrkshots: str
    glbrksaves: str
    glbrksavepct: str
    glpenshots: str
    glpensaves: str
    glpensavepct: str
    glsoshots: str
    glsosaves: str
    glsosavepct: str
    glrecord: str
    glpokechecks: str
    glgc: str
    glgcFC: str
    glprevwins: str
    glprevso: str
    glpkclearzone: str
    glgp: str
    lwgp: str
    rwgp: str
    cgp: str
    dgp: str
    skgp: str
    gamesplayed: str
    gamesCompleted: str
    gamesCompletedFC: str
    skwinpct: str
    glwinpct: str
    lwQuitDisc: str
    rwQuitDisc: str
    cQuitDisc: str
    dQuitDisc: str
    glQuitDisc: str
    skDNF: str
    lwDNF: str
    rwDNF: str
    cDNF: str
    dDNF: str
    glDNF: str
    glDNFmm: str
    playerQuitDisc: str
    playerDNF: str
    xfactor_zoneability_goals: str
    xfactor_zoneability_assists: str
    xfactor_zoneability_saves: str
    xfactor_zoneability_hits: str
    xfactor_zoneability_stick_checks: str
    xfactor_zoneability_times_used: str
    xfactor_superstarability_goals: str
    xfactor_superstarability_assists: str
    xfactor_superstarability_saves: str
    xfactor_superstarability_hits: str
    xfactor_superstarability_stick_checks: str
    favoritePosition: str
    goals: str
    assists: str
    points: str
    pointspg: str
    gwg: str
    plusmin: str
    toi: str
    pim: str
    ppg: str
    shg: str
    penaltyshotgoals: str
    penaltyattempts: str
    penaltyshotpct: str
    offsides: str
    offsidespg: str
    fights: str
    fightswon: str
    fo: str
    fow: str
    fol: str
    fop: str
    hits: str
    hitspg: str
    bs: str
    shots: str
    shotpct: str
    shotspg: str
    shotattempts: str
    shotonnetpct: str
    passes: str
    passattempts: str
    passpct: str
    saucerpasses: str
    dekes: str
    dekesmade: str
    giveaways: str
    takeaways: str
    interceptions: str
    scrnchances: str
    scrngoals: str
    brkgoals: str
    breakaways: str
    breakawaypct: str
    gc: str
    gcFC: str
    hattricks: str
    prevgoals: str
    prevassists: str
    possession: str
    deflections: str
    pkclearzone: str
    penaltiesdrawn: str
    gp: str
    winpct: str
    DNF: str
    name: str


@dataclass
class Player:
    skplayername: str
    gamesplayed: int
    skgoals: int
    skassists: int
    skplusmin: int
    skpim: int
    skhits: int
    glgp: int
    dgp: int
    rwgp: int
    cgp: int
    lwgp: int
    glgaa: float
    glga: int
    glsaves: int
    glsavepct: float
    glso: int
    glsoperiods: int
    blazeId: int
    favoritePosition: str
    name: str


@dataclass
class Record:
    player: MatchPlayerData
    match: Match
    stats_key: str
    stats_value: str
