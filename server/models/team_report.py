from dataclasses import dataclass
from typing import List
from models.game_log import GameLog
from models.teams import TeamSummary
from typing import Dict, Optional


@dataclass
class TeamScoutingData:
    game_logs: List[GameLog]
    team_summary: TeamSummary


@dataclass
class LLMInference:
    prompt: str
    response: str
    inference_at: str
    model: str
    is_primary: bool
    latency_ms: Optional[float] = None


@dataclass
class TeamReport:
    report_id: str
    team_id: str
    team_name: str
    scouting_data: TeamScoutingData
    responses: Dict[str, LLMInference]
    created_at: str
    # TODO: Key (positive) Players
