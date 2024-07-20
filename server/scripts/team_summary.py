from crawlers.tdl.team_summary import get_team_summary
from crawlers.tdl.game_log import get_game_log
from lib_db import db


if __name__ == "__main__":
    print("input team id")
    team_id = input()
    print(f"fetching data for team {team_id}")
    team_summary = get_team_summary(team_id)
    db.write_team_summary(team_id, team_summary)

    game_logs = []
    for game in team_summary.games[:5]:
        game_id = game.game_link.rstrip("/").split("/")[-1]
        game_log = get_game_log(game_id)
        game_logs.append(game_log)
    db.write_game_logs(team_id, game_logs)
