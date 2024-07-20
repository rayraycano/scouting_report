from dataclasses import dataclass
from typing import List, Optional
from models.raw_game import GameDetails
from models.player_stats import PlayerStats


@dataclass
class GameLog:
    game_details: GameDetails
    home_team_stats: List[PlayerStats]
    away_team_stats: List[PlayerStats]
    game_url: str
    youtube_link: Optional[str] = None