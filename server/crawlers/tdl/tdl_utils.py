from typing import Optional, Union
import bs4
from models.player_stats import PlayerStats, PlayerAverages
from models.raw_game import RawGame
from bs4 import BeautifulSoup
from crawlers.bs4_utils import HTML_PARSER
import requests
from datetime import datetime
import re

LEAGUE_NAME = "tdl"


def request_page(url: str) -> BeautifulSoup:
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"failed to request page: {url}")
    soup = BeautifulSoup(response.content, HTML_PARSER)
    title = soup.find("h1")
    if "can't be found" in title.text.lower():
        raise Exception(f"page not found for url: {url}")
    return soup


def convert_date_to_iso8601(date: str):
    """expects date to be formatted like `March 25, 2024`"""
    date_obj = datetime.strptime(date, "%B %d, %Y")
    return date_obj.isoformat()


def get_raw_game(table_row: bs4.element) -> Optional[RawGame]:
    date_td = table_row.find("td", class_="data-date")
    data_home = table_row.find("td", class_="data-home")
    results_td = table_row.find("td", class_="data-results")
    data_away = table_row.find("td", class_="data-away")
    if date_td and results_td:
        results_td_cleaned = results_td.text.replace(" ", "")
        first_result = results_td_cleaned.split("-")[0]
        if not first_result or not first_result.isnumeric():
            return None
        game = RawGame(
            date=date_td.text,
            game_link=results_td.find("a")["href"],
            home_team=data_home.text,
            away_team=data_away.text,
            score=results_td.text,
        )
        return game
    return None


EPSILON = 0.000001


def calculate_rough_per(
    fgm,
    fga,
    steals_pg,
    tpm,
    ftm,
    fta,
    blocks_pg,
    reb_pg,
    assists_pg,
    fouls_pg,
    to_pg,
    g,
) -> Optional[float]:
    """
    Notes:
        - constants derived from here: https://www.sportsbettingdime.com/guides/how-to/calculate-per/
        - we consider each player to play 36 minutes per game
        - we approximate a defensive rebound to offensive rebound ratio
    """
    try:
        reb = round(reb_pg * g)
        steals = round(steals_pg * g)
        assists = round(assists_pg * g)
        blocks = round(blocks_pg * g)
        fouls = round(fouls_pg * g)
        to = round(to_pg * g)
        if g == 0:
            return 0
        MINUTES_PER_GAME = 36
        DREB_FRACTION = 7.0 / 10
        fg_miss = fga - fgm
        ft_miss = ftm - fta
        minutes = MINUTES_PER_GAME
        dreb = reb * DREB_FRACTION
        oreb = reb * (1 - DREB_FRACTION)
        to_multiply = [
            (fgm, 85.910),
            (steals, 53.897),
            (tpm, 51.757),
            (ftm, 46.845),
            (blocks, 39.190),
            (oreb, 39.190),
            (assists, 34.677),
            (dreb, 14.707),
            (fouls, -17.174),
            (ft_miss, -20.091),
            (fg_miss, -39.190),
            (to, -53.897),
        ]
        numerator = 0
        for stat, multiplier in to_multiply:
            numerator += stat * multiplier
        return numerator / minutes
    except Exception as e:
        return None


def get_player_averages(table_row: bs4.element) -> PlayerAverages:
    games_played = extract_data(table_row, "G")
    points_pg = extract_data(table_row, "PPG")
    assists_pg = extract_data(table_row, "APG")
    fgm = extract_data(table_row, "FGM")
    fga = extract_data(table_row, "FGA")
    tpm = extract_data(table_row, "3PM")
    ftm = extract_data(table_row, "FTM")
    fta = extract_data(table_row, "FTA")
    steals_pg = extract_data(table_row, "SPG")
    blocks_pg = extract_data(table_row, "BPG")

    # calculations
    points = round(points_pg * games_played)
    ts = points / (2 * (fga + 0.44 * fta) + EPSILON)
    efg = (fgm + 0.5 * tpm) / (fga + EPSILON)
    turnovers_pg = extract_data(table_row, "TPG")
    rebounds_pg = extract_data(table_row, "RPG")
    personal_fouls_pg = extract_data(table_row, "FPG")
    ato = assists_pg / (turnovers_pg + EPSILON)
    rough_per = calculate_rough_per(
        fgm=fgm,
        fga=fga,
        steals_pg=steals_pg,
        tpm=tpm,
        ftm=ftm,
        fta=fta,
        blocks_pg=blocks_pg,
        reb_pg=rebounds_pg,
        assists_pg=assists_pg,
        fouls_pg=personal_fouls_pg,
        to_pg=turnovers_pg,
        g=games_played,
    )

    player = PlayerAverages(
        player_name=extract_data(table_row, "Player"),
        player_id=extract_player_id(table_row),
        games_played=games_played,
        points_pg=points_pg,
        rebounds_pg=rebounds_pg,
        assists_pg=assists_pg,
        blocks_pg=blocks_pg,
        steals_pg=steals_pg,
        fgm=fgm,
        fga=fga,
        fg_percent=extract_data(table_row, "FG%"),
        tpm=tpm,
        tpa=extract_data(table_row, "3PA"),
        tp_percent=extract_data(table_row, "3P%"),
        ftm=ftm,
        fta=fta,
        ft_percent=extract_data(table_row, "FT%"),
        turnovers_pg=turnovers_pg,
        personal_fouls_pg=personal_fouls_pg,
        true_shooting_percent=ts,
        effective_fgp=efg,
        assist_turnover_ratio=ato,
        rough_per=rough_per,
    )
    return player


def get_player_stats(table_row: bs4.element) -> PlayerStats:
    player = PlayerStats(
        player_name=extract_data(table_row, "Player"),
        player_id=extract_player_id(table_row),
        points=extract_data(table_row, "PTS"),
        rebounds=extract_data(table_row, "REB"),
        assists=extract_data(table_row, "AST"),
        steals=extract_data(table_row, "STL"),
        blocks=extract_data(table_row, "BLK"),
        fgm=extract_data(table_row, "FGM"),
        fga=extract_data(table_row, "FGA"),
        fg_percent=extract_data(table_row, "FG%"),
        tpm=extract_data(table_row, "3PM"),
        tpa=extract_data(table_row, "3PA"),
        tp_percent=extract_data(table_row, "3P%"),
        ftm=extract_data(table_row, "FTM"),
        fta=extract_data(table_row, "FTA"),
        ft_percent=extract_data(table_row, "FT%"),
        turnovers=extract_data(table_row, "TO"),
        personal_fouls=extract_data(table_row, "PF"),
    )
    return player


def extract_player_id(player_row: bs4.element) -> str:
    try:
        player_href = player_row.find("td", {"data-label": "Player"}).find("a")["href"]
        player_id = player_href.rstrip("/").split("/")[-1]
        return player_id
    except Exception as e:
        print(f"failed to find href for player: {e}")
        print(f"player row: {player_row}")


def extract_data(
    player_row: bs4.element, data_label: str
) -> Optional[Union[float, int]]:
    cell = player_row.find("td", {"data-label": data_label})
    try:
        if cell:
            if data_label in ["FG%", "3P%", "FT%"] or "PG" == data_label[-2:]:
                return float(cell.text)
            if data_label == "Player":
                return cell.text.strip()
            cleaned = re.sub("[^0-9]", "", cell.text)
            if not cleaned:
                return 0
            return int(cleaned)
        return None
    except Exception as e:
        print(f"failed to extract data with exception: {e}")
        print(f"cell: {cell}")
        raise e
