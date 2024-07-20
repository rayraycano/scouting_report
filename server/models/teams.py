from dataclasses import dataclass
from typing import List, Optional
from models.player_stats import PlayerAverages
from models.raw_game import RawGame


@dataclass
class Team:
    team_id: str
    name: str
    league: str
    division: Optional[str] = None
    url: Optional[str] = None


@dataclass
class TeamSummary:
    # TODO: remove this once we purge bad data
    games: List[RawGame]
    player_averages: List[PlayerAverages]
    snapshot_at: str  # datetime.isoformat()
    team: Optional[Team] = None
