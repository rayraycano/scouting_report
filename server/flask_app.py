from flask import Flask, request, jsonify, abort
import time
from dataclasses import asdict
import json
import os
from models.teams import Team
from lib_db import db as scout_db
from product_layer.data_retrieval import get_team_scouting_input_data
from product_layer.report_retrieval import get_scouting_report_for_team

NAME = "Raymond Cheong Cano"
app = Flask(__name__)

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
def get_teams():
    teams = scout_db.get_teams_for_league(league_id=LEAGUE_ID)
    formatted_teams = []
    for t in teams:
        json_team = asdict(t)
        formatted_teams.append(json_team)
    response = jsonify({"teams": formatted_teams})
    return response


@app.route("/teams/report/generate", methods=["POST"])
def generate_team_report():
    req_body = request.json
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
def get_team_summary():
    team_id = request.args.get("team_id")
    data = get_team_scouting_input_data(team_id)
    return jsonify(asdict(data))


@app.route("/", methods=["POST"])
def update_db():
    # Logging the request and JSON body
    key = request.json.get("key")
    value = request.json.get("value")
    db[key] = value
    # Return the updated db as a JSON
    return jsonify(db)


@app.route("/players/list", methods=["GET"])
def get_player_names():
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
