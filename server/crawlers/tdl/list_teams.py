from typing import List
from models.teams import Team
from bs4 import BeautifulSoup
from crawlers.tdl.tdl_utils import request_page
from crawlers.tdl.team_summary import get_team

STANDINGS_HOME_URL = "https://tdlbasketball.com/teams-standings/"


def get_teams() -> List[Team]:
    soup = request_page(STANDINGS_HOME_URL)
    teams = []
    standings_links = []
    for li in soup.find_all("li", class_="has-small-font-size"):
        standings_links.append(li.find("a")["href"])
    for l in standings_links:
        standing_soup = request_page(l)
        teams.extend(get_teams_from_standings(standing_soup))
    return teams


def get_teams_from_standings(soup: BeautifulSoup) -> List[Team]:
    links: List[str] = []
    rows = soup.find("table", class_="sp-league-table").find("tbody").find_all("tr")
    teams = []
    for r in rows:
        team_link = r.find("td", class_="data-name").find("a")["href"]
        links.append(team_link)
    for link in links:
        soup = request_page(link)
        team_id = link.rstrip("/").split("/")[-1]
        team = get_team(soup, team_id)
        teams.append(team)
    return teams
