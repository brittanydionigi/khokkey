from pymongo import MongoClient
client = MongoClient()

teamsdb = client['teams']
teams_table = teamsdb['teams']

def get_game_info(teams, info):
  game_meta = { "date": info.findAll('tr')[3].find('td').text }
  game_meta["score"] = []
  game_meta["team_abbrs"] = {};


  # Set playoffs data if applicable
  playoff_series = info.findAll('tr')[2].find('td')
  if playoff_series.text and "Winter Classic" not in playoff_series.text:
    game_meta["playoffs"] = { "series": playoff_series.text }
  if playoff_series.text and "Winter Classic" in playoff_series.text:
    game_meta["series"] = playoff_series.text

  # Iterate over home/away teams
  for t in teams:
    team_name = teams[t].findAll('tr')[-1].find('td').text

    # Montreal Canadien games have different formatting
    # This standardizes our split & team name
    team_name = team_name.replace("Match/Game", "Game").split('Game')
    game_meta[t] = team_name[0].title()

    if game_meta[t] == "Canadiens Montreal":
      game_meta[t] = "Montreal Canadiens"

    team_abbr = teams_table.find({ "team": game_meta[t] })
    team_abbr = team_abbr[0]["abbr"]
    game_meta["team_abbrs"][t] = team_abbr

    game_meta["score"].append({"team": game_meta[t], "score": 0 })
    if "playoffs" in game_meta:
      # TO DO: should only need to do this once, not twice for both teams
      game_meta["playoffs"]["game_number"] = team_name[1][1:2]

  return game_meta



