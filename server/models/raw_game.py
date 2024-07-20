from dataclasses import dataclass
from typing import Optional


@dataclass
class RawGame:
    """
    models the table that is like
    date home X-Y away

    if X > y, home team won
    """

    date: str
    home_team: str
    score: str
    away_team: str
    game_link: str
    season: Optional[str] = None


@dataclass
class Score:
    home_team_points: int
    away_team_points: int


@dataclass
class GameDetails:
    date: str
    home_team_id: str
    away_team_id: str
    score: Optional[Score]
    season: Optional[str] = None
