from dataclasses import dataclass
from typing import Optional


@dataclass
class PlayerAverages:
    player_name: str
    player_id: str
    games_played: int
    # averages
    points_pg: float
    rebounds_pg: float
    assists_pg: float
    steals_pg: float
    blocks_pg: float
    turnovers_pg: float
    personal_fouls_pg: float
    # totals
    fgm: int
    fga: int
    fg_percent: float
    tpm: int
    tpa: int
    tp_percent: float
    ftm: int
    fta: int
    ft_percent: float
    # advanced/calculations
    true_shooting_percent: float
    effective_fgp: float
    assist_turnover_ratio: float
    rough_per: Optional[float] = None


@dataclass
class PlayerStats:
    player_name: str
    points: int
    rebounds: int
    assists: int
    steals: int
    blocks: int
    fgm: int
    fga: int
    fg_percent: float
    tpm: int
    tpa: int
    tp_percent: float
    ftm: int
    fta: int
    ft_percent: float
    turnovers: int
    personal_fouls: int
    # TODO: remove this once we purge bad data
    player_id: str = ""
