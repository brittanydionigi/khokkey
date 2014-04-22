from events import temp_game_rosters
from events import game_data

# Standard format: CBJ #17 DUBINSKY
def parse_player(team_player):
  player = team_player[4:]
  player_number = team_player[5:7].strip(' \t\n\r')
  team = team_player[:3]
  if team == game_data["team_abbrs"]["away_team"]:
    for i, roster_spot in enumerate(temp_game_rosters["visitor_roster"]):
      if player_number == roster_spot["number"]:
        player = roster_spot
  else:
    for i, roster_spot in enumerate(temp_game_rosters["home_roster"]):
      if player_number == roster_spot["number"]:
        player = roster_spot

  return { "team": team, "player": player}


