from concurrent.futures import ThreadPoolExecutor
from lib_db import db
from product_layer.data_retrieval import get_team_scouting_input_data
from crawlers.tdl.list_teams import get_teams

teams = [
    "happy-hour",
    "manhattan-elite-d3",
    "opp-pack-d3",
    "spark-plugs",
    "team-texas",
    "tx-thunder-d1",
    "the-quinnterns-d3",
]


def backfill_teams_v2():
    teams = get_teams()
    print(len(teams))
    db.write_teams_for_league("tdl", teams)


def backfill_teams():
    success = 0
    teams = db.get_teams_for_league("tdl")
    executor = ThreadPoolExecutor(max_workers=5)
    futures = {}
    for t in teams:
        f = executor.submit(
            get_team_scouting_input_data, t.team_id, **dict(days_fresh_requirement=0)
        )
        futures[f] = t.team_id
    failed = []
    for t in teams:
        try:
            get_team_scouting_input_data(t.team_id, days_fresh_requirement=0)
            success += 1
        except Exception as e:
            print(f"failed to backfill team {t}: {e}")
            failed.append(t.team_id)
    print(f'failures: {", ". join(failed)}')
    print(f"finished backfilling {success} teams")


if __name__ == "__main__":
    backfill_teams()
