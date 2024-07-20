from bs4 import BeautifulSoup
from typing import List, Optional
from crawlers.tdl.tdl_utils import (
    request_page,
    get_player_stats,
    convert_date_to_iso8601,
)
from models.game_log import GameLog
from models.raw_game import RawGame, GameDetails, Score
from models.player_stats import PlayerStats

EVENT_URL = "https://tdlbasketball.com/event/"


def get_game_log(event_id: str) -> GameLog:
    url = f"{EVENT_URL}{event_id}"
    soup = request_page(url)

    youtube_link = soup.find("iframe")
    if youtube_link:
        youtube_link = youtube_link.get("src", None)
    game_details = parse_game_table(soup)
    home_team_player_stats = parse_player_stats(soup, 0)
    away_team_player_stats = parse_player_stats(soup, 1)
    return GameLog(
        game_details=game_details,
        home_team_stats=home_team_player_stats,
        away_team_stats=away_team_player_stats,
        youtube_link=youtube_link,
        game_url=url,
    )


def parse_game_table(soup: BeautifulSoup) -> GameDetails:
    game_table = soup.find("table", class_="sp-event-details")
    table_body = game_table.find("tbody")
    # order: date / time / league / season
    data = table_body.find_all("td")
    raw_date = data[0].text
    season = data[-1].text
    # teams and score
    score_table = soup.find("table", class_="sp-event-results")
    team_names = score_table.find_all("td", class_="data-name")
    home_team_url = team_names[0].find("a")["href"]
    away_team_url = team_names[1].find("a")["href"]
    home_team_id = home_team_url.split("/")[-2]
    away_team_id = away_team_url.split("/")[-2]
    points = score_table.find_all("td", class_="data-points")
    try:
        home_team_points = int(points[0].text)
        away_team_points = int(points[1].text)
        score = Score(
            home_team_points=home_team_points, away_team_points=away_team_points
        )
    except Exception as e:
        score = None

    return GameDetails(
        date=convert_date_to_iso8601(raw_date),
        home_team_id=home_team_id,
        away_team_id=away_team_id,
        score=score,
        season=season,
    )


def parse_player_stats(soup: BeautifulSoup, idx: int) -> List[PlayerStats]:
    # will this work?
    player_average_table = soup.find_all("table", class_="sp-event-performance")[idx]
    table_body = player_average_table.find("tbody")
    player_stats = []
    for tr in table_body.find_all("tr"):
        player = get_player_stats(tr)
        player_stats.append(player)
    return player_stats
