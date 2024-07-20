from typing import List
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from models.team_report import TeamScoutingData
from models.game_log import GameLog
from crawlers.tdl.team_summary import get_team_summary
from crawlers.tdl.game_log import get_game_log
from lib_db import db
from datetime import datetime


def get_team_scouting_input_data(
    team_id: str, games_back: int = 10, days_fresh_requirement: int = 3
) -> TeamScoutingData:
    # TODO: if the season is just starting, maybe we should look back at
    # historical games
    most_recent = db.get_most_recent_update_for_team(team_id)
    if not most_recent or is_data_stale(most_recent, days_fresh_requirement):
        ensure_scouting_data_for_team(team_id)
    team_summary = db.get_team_summary(team_id)
    game_logs = db.get_game_logs(team_id, games_back)
    return TeamScoutingData(game_logs=game_logs, team_summary=team_summary)


def ensure_scouting_data_for_team(team_id):
    print(f"ensuring data for {team_id}")
    summary = get_team_summary(team_id)
    game_logs: List[GameLog] = []
    # TODO: paramaterize this in a class
    executor = ThreadPoolExecutor(max_workers=5)
    future_to_game_id = {}
    for raw_game in summary.games:
        event_id = raw_game.game_link.rstrip("/").split("/")[-1]
        job = executor.submit(get_game_log, event_id)
        future_to_game_id[job] = event_id
    for future in concurrent.futures.as_completed(future_to_game_id):
        game_log = future.result()
        game_logs.append(game_log)

    game_logs = sorted(game_logs, key=lambda x: x.game_details.date)
    # write order guarantees we referesh data when necessary
    db.write_game_logs(team_id, game_logs)
    db.write_team_summary(team_id, summary)


def is_data_stale(most_recent: datetime, days_fresh_requirement: int) -> bool:
    today = datetime.now()
    difference = today - most_recent
    return difference.days >= days_fresh_requirement
