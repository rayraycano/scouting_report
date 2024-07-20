from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from models.teams import TeamSummary, Team
from models.game_log import GameLog
from models.team_report import TeamReport
from dataclasses import asdict
import dacite
import json
from os import path
import os


def _league_folderpath(league_id: str) -> str:
    return path.join("db", "leagues", league_id)


def _team_scouting_report_folderpath(team_id) -> str:
    return path.join("db", "teams", team_id, "reports")


def _game_log_folderpath(team_id: str) -> str:
    return path.join("db", "teams", team_id, "game_logs")


def _team_summary_folderpath(team_id: str) -> str:
    return path.join("db", "teams", team_id, "summaries")


def get_most_recent_update_for_team(team_id: str) -> Optional[datetime]:
    filename = _get_most_recent_summary_filename(team_id)
    if filename is None:
        return None
    return datetime.fromisoformat(filename)


def _get_most_recent_summary_filename(team_id: str) -> Optional[str]:

    folderpath = _team_summary_folderpath(team_id)
    if not path.exists(folderpath):
        return None
    # filenames are timestamps
    filenames = os.listdir(folderpath)
    if len(filenames) == 0:
        return None
    sorted_filenames = sorted(filenames)
    return sorted_filenames[-1]


def write_team_scouting_report(report: TeamReport):
    folderpath = _team_scouting_report_folderpath(report.team_id)
    if not path.exists(folderpath):
        os.makedirs(folderpath)
    with open(path.join(folderpath, report.report_id), "w") as f:
        json.dump(asdict(report), f, indent=2)


def get_most_recent_report(team_id: str) -> Optional[TeamReport]:
    folderpath = _team_scouting_report_folderpath(team_id)
    if not path.exists(folderpath):
        return None
    most_recent_report = None
    most_recent_report_date = "1"
    for report_id in os.listdir(folderpath):
        with open(path.join(folderpath, report_id)) as f:
            report_json = json.load(f)
            report = dacite.from_dict(TeamReport, report_json)
            if most_recent_report_date < report.created_at:
                most_recent_report = report
                most_recent_report_date = report.created_at
    return most_recent_report


def get_game_logs(team_id: str, max_num_games: int) -> List[GameLog]:
    folderpath = _game_log_folderpath(team_id)
    if not path.exists(folderpath):
        return []
    files = os.listdir(folderpath)
    # isoformat datetimes
    sorted_filenames = sorted(files)
    num_to_return = min(max_num_games, len(files))
    filtered_filenames = sorted_filenames[-num_to_return:]
    game_logs = []
    for fn in filtered_filenames:
        with open(path.join(folderpath, fn)) as f:
            game_log_json = json.load(f)
            game_log = dacite.from_dict(GameLog, game_log_json)
            game_logs.append(game_log)

    return game_logs


def get_team_summary(team_id: str) -> TeamSummary:
    filename = _get_most_recent_summary_filename(team_id)
    if not filename:
        raise Exception("no summary found for team_id")
    folderpath = _team_summary_folderpath(team_id)
    with open(path.join(folderpath, filename)) as f:
        team_summary_json = json.load(f)
        return dacite.from_dict(TeamSummary, team_summary_json)


def write_game_logs(team_id: str, game_logs: List[GameLog]):
    folderpath = _game_log_folderpath(team_id)

    if not path.exists(folderpath):
        os.makedirs(folderpath)
    for game_log in game_logs:
        filepath = path.join(folderpath, game_log.game_details.date)
        with open(filepath, "w") as f:
            json.dump(asdict(game_log), f, indent=2)


def write_team_summary(team_id: str, team_summary: TeamSummary):
    folderpath = _team_summary_folderpath(team_id)
    if not path.exists(folderpath):
        os.makedirs(folderpath)
    filepath = path.join(folderpath, team_summary.snapshot_at)

    with open(filepath, "w") as f:
        json.dump(asdict(team_summary), f, indent=2)


@dataclass
class LeagueSnapshot:
    teams: List[Team]
    created_at: str


LEAGUE_SNAPSHOT_FILENAME = "snapshot.json"


def write_teams_for_league(league_id: str, teams: List[Team]):
    folderpath = _league_folderpath(league_id)
    if not path.exists(folderpath):
        os.makedirs(folderpath)
    snapshot = LeagueSnapshot(teams, datetime.now().isoformat())
    with open(path.join(folderpath, LEAGUE_SNAPSHOT_FILENAME), "w") as f:
        json.dump(asdict(snapshot), f, indent=2)


def get_teams_for_league(league_id: str) -> List[Team]:
    folderpath = _league_folderpath(league_id)
    if not path.exists(folderpath):
        return []
    with open(path.join(folderpath, LEAGUE_SNAPSHOT_FILENAME)) as f:
        snapshot_json = json.load(f)
        snapshot_details = dacite.from_dict(LeagueSnapshot, snapshot_json)
        return snapshot_details.teams
