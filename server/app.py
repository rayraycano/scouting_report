from quart import Quart, request, jsonify, abort, websocket
import random
from copy import deepcopy
import json
import time
from dataclasses import asdict
import os
from lib_db import db as scout_db
from product_layer.data_retrieval import get_team_scouting_input_data
from product_layer.report_retrieval import get_scouting_report_for_team, ReportRetriever
from product_layer.report import ReportGenerator
from llms.api import init_models, primary_model_name, secondary_model_names

NAME = "Raymond Cheong Cano"
app = Quart(__name__)

# Simulating the database object from the original JS code
db = {
    "message": "Welcome to the SEC",
    "school": "University of Texas, Austin",
    "father": "LSU",
    "specialty": "Volleyball",
    "isFootballSchool": False,
    "isTexasBack": "always",
}

LEAGUE_ID = "tdl"


@app.route("/teams/list", methods=["GET"])
async def get_teams():
    teams = scout_db.get_teams_for_league(league_id=LEAGUE_ID)
    formatted_teams = []
    for t in teams:
        json_team = asdict(t)
        formatted_teams.append(json_team)
    response = jsonify({"teams": formatted_teams})
    return response


report_retriever = ReportRetriever(
    ReportGenerator(
        models=init_models(),
    ),
    scout_db,
)


@app.websocket("/teams/report/stream")
async def stream_team_report():
    # TODO:
    # - add model id or a default
    # - instantiate classes
    req_body = await websocket.receive_json()
    team_id = req_body.get("team_id", None)
    is_secondary_request = req_body.get("is_secondary_request", False)
    if not team_id:
        abort(400, "team_id must be non null string")
    model_id = primary_model_name()
    if is_secondary_request:
        model_id = random.choice(secondary_model_names())
    for current_report in report_retriever.stream_scouting_report_for_team(
        team_id, model_id
    ):
        await websocket.send(
            json.dumps(
                {
                    "report_id": current_report.report_id,
                    "created_at": current_report.created_at,
                    "responses": {
                        k: asdict(v) for k, v in current_report.responses.items()
                    },
                }
            )
        )


@app.route("/teams/report/generate", methods=["POST"])
async def generate_team_report():
    req_body = await request.get_json()
    team_id = req_body.get("team_id", None)
    if not team_id:
        abort(400, "team_id must be non null string")
    t = time.time()
    report = get_scouting_report_for_team(team_id)
    latency_seconds = time.time() - t
    print(f"generated report in {latency_seconds} seconds")
    return jsonify(
        {
            "report_id": report.report_id,
            "created_at": report.created_at,
            "responses": report.responses,
        }
    )


@app.route("/teams", methods=["GET"])
async def get_team_summary():
    team_id = request.args.get("team_id")
    data = get_team_scouting_input_data(team_id)
    return jsonify(asdict(data))


@app.route("/", methods=["POST"])
async def update_db():
    # Logging the request and JSON body
    key = request.json.get("key")
    value = request.json.get("value")
    db[key] = value
    # Return the updated db as a JSON
    return jsonify(db)


@app.route("/players/list", methods=["GET"])
async def get_player_names():
    names = os.listdir("db")
    formatted_names = [n.replace("-", " ").title() for n in names]
    return jsonify(formatted_names)


# @app.route("/players", methods=["GET"])
# def players_get():
#     player_name = request.args.get("player_name")
#     print(player_name)
#     player_data = get_player_data(player_name)
#     return jsonify(player_data)
#
#
# @app.route("/api", methods=["GET"])
# def get_db():
#     print("visitor!")
#     result = get_player_data(NAME)
#     print(result)
#
#     # Return the db as a JSON
#     return jsonify(db)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3001))
    app.run(port=port, debug=True)
