from bs4 import BeautifulSoup
import requests
from crawlers.tdl.tdl_utils import get_player_averages, get_raw_game
import datetime
from models.teams import TeamSummary, Team
from crawlers.tdl.tdl_utils import request_page, LEAGUE_NAME


N_GAMES_BACK = 5
FILENAME = "team_data.json"


def get_team_url(team_id: str) -> str:
    return f"https://tdlbasketball.com/team/{team_id}/"


def get_team(soup: BeautifulSoup, team_id: str) -> Team:
    """Expects the team landing page"""
    team_url = get_team_url(team_id)
    team_details = soup.find("dl", class_="sp-team-details")
    divisions = team_details.find("dd").text
    curr_division = divisions.split(",")[0]

    team = Team(
        team_id=team_id,
        name=soup.find("h1", class_="entry-title").text,
        url=team_url,
        league=LEAGUE_NAME,
        division=curr_division,
    )
    return team


def get_team_summary(team_id: str) -> TeamSummary:
    """
    Fetches Team summary based on the team id
    :param team_id:
    :return:
    """
    team_url = get_team_url(team_id)
    soup = request_page(team_url)
    team = get_team(soup, team_id)
    player_average_table = soup.find("table", class_="sp-player-list")
    player_averages = []
    table_body = player_average_table.find("tbody")
    for tr in table_body.find_all("tr"):
        player_avg = get_player_averages(tr)
        player_averages.append(player_avg)
    games_table = soup.find("table", class_="sp-event-list")
    games_table_body = games_table.find("tbody")
    games = []
    for tr in games_table_body.find_all("tr"):
        maybe_game = get_raw_game(tr)
        if maybe_game:
            games.append(maybe_game)
        else:
            print(f"skipping game: {tr}")
    dt = datetime.datetime.now()

    return TeamSummary(
        team=team,
        games=games,
        player_averages=player_averages,
        snapshot_at=dt.isoformat(),
    )
