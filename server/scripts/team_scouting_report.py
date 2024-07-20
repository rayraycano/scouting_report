from product_layer.report import ReportGenerator
from llms.gpt4 import GPT4, _GPT_4_MODEL_ID
from llms.baseten import BasetenModel, _BASETEN_MODEL_ID
from llms.modal import ModalModel
from product_layer.data_retrieval import get_team_scouting_input_data
from lib_db import db

if __name__ == "__main__":
    print("input team id")
    team_id = input()
    gpt4 = GPT4(_GPT_4_MODEL_ID)
    baseten_mixtral = BasetenModel(_BASETEN_MODEL_ID)
    modal_mixtral = ModalModel()
    rg = ReportGenerator(models=[gpt4, baseten_mixtral, modal_mixtral])
    data = get_team_scouting_input_data(team_id, games_back=5)
    reports = rg.generate_team_scouting_report(
        team_id=team_id,
        data=data,
    )
    db.write_team_scouting_report(reports)
    print(f"finished generating report for {team_id}")
