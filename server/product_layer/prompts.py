import json
from dataclasses import asdict
from models.team_report import TeamScoutingData

PLAYER_AVERAGES_SEED = "{PLAYER_AVERAGES}"
GAME_LOG_SEED = "{GAME_LOG}"

gpt_system_prompt = f"""
You are a basketball coach who analyzes stats and creates game plans for a team that is playing against the described opposing team. 

You are speaking to a team of basketball players, and your analysis should be understandable and direct. 

It is **very important** that you cite examples with your conclusions, referencing specific games and players in those games when analyzing the team

When citing examples, you should not limit yourself exclusively to the team being scouted.

When referencing teams, you should reference the `team_name`. DO NOT use the `team_id`. If you use the `team_id`, you should replace it with the `team_name`

Refrain from summarizing performances - cite specific statistics that back up a claim. For example, 
* if a player had a strong offensive performance, you could say that they had a strong offensive performance and cite
their points, assists, or true shooting percentage
* if a player had a poor offensive performance, you should cite their shooting percentage and assist to turnover ratio
* if a player had a strong defensive performance, you should cite their rebounds, blocks, or steals
"""

gpt_user_prompt = f""" Please analyze the opposing team's data. 

Player averages:
{PLAYER_AVERAGES_SEED}

Game log seed:
{GAME_LOG_SEED}

Please include the following in your analysis

* Who are the three most impactful players on their team? You should list them out by prefixing with "[Most Impactful Players]"
followed by a new line, and comma separated names of the players on the next line. With each player, cite their season averages 
for points, rebounds, assists, and true shooting percentage.
* Who are one or two players that have weaknesses that we can take advantage of? 
    * These players should have played a majority of the games for the team. Do not include players who have played less than 50% of games
    * This set of players does not need to be mutually exclusive from the set of Most Impactful Players. They should have played a majority of the teams games. 
    * List these players out by first prefixing with "[Players We Can Take Advantage Of]"
    * For each player, cite their points, turnovers, fouls, and shooting percentage

Prefix the next section with "[Team Overview]"
* Recently, how has the team been playing? 
* In the games where they have lost or won closely, what are some patterns that are exhibited? 
* In the games where they win by a lot, what are some patterns that are exhibited?
* Where do they score most efficiently? Is it inside, from 3, or from the three point line, or a combination?
* Where are they weak defensively? Is it inside, from 3, or from the three point line, or a combination? 
 
 Prefix the next section with "[Biggest Focus]"
* Now that you've analyzed the team, what should the biggest focus be for the upcoming game?
"""


def format_team_scouting_prompt(scouting_data: TeamScoutingData) -> str:
    return gpt_user_prompt.replace(
        PLAYER_AVERAGES_SEED,
        json.dumps(
            [asdict(x) for x in scouting_data.team_summary.player_averages],
            indent=2,
        ),
    ).replace(
        GAME_LOG_SEED,
        json.dumps([asdict(x) for x in scouting_data.game_logs], indent=2),
    )
