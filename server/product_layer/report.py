from typing import List, Optional, Set, Iterator, Dict
from lib_db import db
import threading
from product_layer.data_retrieval import get_team_scouting_input_data
from models.team_report import TeamReport
from product_layer.prompts import format_team_scouting_prompt, gpt_system_prompt
from uuid import uuid4
from models.team_report import LLMInference, TeamScoutingData
from datetime import datetime
from llms.interface import LLM
from llms.gpt4 import GPT4, _GPT_4_MODEL_ID


from llms.baseten import BasetenModel, _BASETEN_MODEL_ID
import time


class ReportGenerator:
    def __init__(self, models: List[LLM]):
        self.models = models

    def stream_report_for_model(
        self,
        team_id: str,
        data: TeamScoutingData,
        model_id: str,
        existing_report: Optional[TeamReport] = None,
    ) -> Iterator[TeamReport]:
        """so the caller requests a report
        opens a websocket with the details to run this
        the report is created
        the report is yielded with the updated information
        """

        user_prompt = format_team_scouting_prompt(data)
        timestamp = datetime.now().isoformat()
        for m in self.models:
            print(m.get_name())
        maybe_models = [x for x in self.models if x.get_name() == model_id]
        if len(maybe_models) == 0:
            raise Exception(f"invalid model id: {model_id}")
        model = maybe_models[0]
        inference = LLMInference(
            prompt=user_prompt,
            response="",
            inference_at=timestamp,
            model=model.get_name(),
            is_primary=self.models[0].get_name() == model.get_name(),
        )
        report_id = uuid4()
        if existing_report:
            report = existing_report
        else:
            report = TeamReport(
                report_id=report_id.hex,
                team_id=team_id,
                team_name=data.team_summary.team.name,
                scouting_data=data,
                responses={},
                created_at=datetime.now().isoformat(),
            )
        report.responses[model.get_name()] = inference

        for text in model.request_stream(gpt_system_prompt, user_prompt):
            if text:
                inference.response = "".join([inference.response, text])
                print(inference.response)
            yield report

    def create_completions_multithreaded(
        self, model_filter, user_prompt
    ) -> Dict[str, LLMInference]:
        responses = {}
        timestamp = datetime.now().isoformat()

        def do_request(model, system, user):
            print(model.get_name())
            start = time.time()
            result = model.request(system, user)
            elapsed_ms = (time.time() - start) * 1000
            responses[model.get_name()] = LLMInference(
                prompt=user,
                response=result,
                inference_at=timestamp,
                model=model.get_name(),
                is_primary=self.models[0].get_name() == model.get_name(),
                latency_ms=elapsed_ms,
            )
            print(result)

        threads = []
        for m in self.models:
            if model_filter and m.get_name() not in model_filter:
                continue
            t = threading.Thread(
                target=do_request, args=(m, gpt_system_prompt, user_prompt)
            )
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        return responses

    def generate_team_scouting_report(
        self,
        team_id: str,
        data: TeamScoutingData,
        model_filter: Optional[Set[str]] = None,
    ):
        user_prompt = format_team_scouting_prompt(data)
        responses = self.create_completions_multithreaded(model_filter, user_prompt)
        report_id = uuid4()
        report = TeamReport(
            report_id=report_id.hex,
            team_id=team_id,
            team_name=data.team_summary.team.name,
            scouting_data=data,
            responses=responses,
            created_at=datetime.now().isoformat(),
        )
        return report

    def add_responses_to_report(
        self, model_filter: List[str], report: TeamReport
    ) -> TeamReport:
        user_prompt = format_team_scouting_prompt(report.scouting_data)
        responses = self.create_completions_multithreaded(model_filter, user_prompt)
        report.responses = {**report.responses, **responses}
        return report


def generate_team_scouting_report(team_id: str) -> TeamReport:
    data = get_team_scouting_input_data(team_id, games_back=5)
    models = [
        GPT4(_GPT_4_MODEL_ID),
        BasetenModel(_BASETEN_MODEL_ID),
    ]
    rg = ReportGenerator(models)
    report = rg.generate_team_scouting_report(team_id, data)
    db.write_team_scouting_report(report)
    return report
