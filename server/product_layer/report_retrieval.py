from typing import Iterable
from lib_db import db
from models.team_report import TeamReport
from datetime import datetime
from product_layer.data_retrieval import is_data_stale, get_team_scouting_input_data
from product_layer.report import generate_team_scouting_report, ReportGenerator


class ReportRetriever:
    def __init__(self, report_generator: ReportGenerator, db):
        self.report_generator = report_generator
        self.db = db

    def stream_scouting_report_for_team(
        self,
        team_id: str,
        model_id: str,
        days_fresh_requirement: int = 3,
    ) -> Iterable[TeamReport]:
        most_recent_report = self.db.get_most_recent_report(team_id)
        if most_recent_report is None or is_data_stale(
            datetime.fromisoformat(most_recent_report.created_at),
            days_fresh_requirement,
        ):
            data = get_team_scouting_input_data(team_id, days_fresh_requirement)
            for report in self.report_generator.stream_report_for_model(
                team_id,
                data,
                model_id,
            ):
                yield report
                most_recent_report = report
            self.db.write_team_scouting_report(most_recent_report)
        else:
            yield most_recent_report

    def get_scouting_report_for_team(
        self, team_id: str, days_fresh_requirement: int = 3
    ):
        most_recent_report = db.get_most_recent_report(team_id)
        if most_recent_report is None or is_data_stale(
            datetime.fromisoformat(most_recent_report.created_at),
            days_fresh_requirement,
        ):
            data = get_team_scouting_input_data(
                team_id,
                days_fresh_requirement,
            )
            most_recent_report = self.report_generator.generate_team_scouting_report(
                team_id, data
            )
            db.write_team_scouting_report(most_recent_report)
        return most_recent_report


def get_scouting_report_for_team(
    team_id: str, days_fresh_requirement: int = 3
) -> TeamReport:
    # TODO: unify the days_fresh_requirement to one SOT default
    most_recent_report = db.get_most_recent_report(team_id)
    if most_recent_report is None or is_data_stale(
        datetime.fromisoformat(most_recent_report.created_at), days_fresh_requirement
    ):
        # also writes to the db
        most_recent_report = generate_team_scouting_report(team_id)
    return most_recent_report
