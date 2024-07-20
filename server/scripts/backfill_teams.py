from lib_db import db
from crawlers.tdl.list_teams import get_teams


def backfill_teams(league_id: str):
    if league_id == "tdl":
        teams = get_teams()
        print(len(teams))
        db.write_teams_for_league("tdl", teams)


if __name__ == "__main__":
    print("input the league_id")
    input_league_id = input()
    backfill_teams(input_league_id)
