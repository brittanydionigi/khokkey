

def parse_other_shot_info(details):
  shot_info = {}
  info = details.contents if len(details.contents) > 1 else details.text
  team = info[:3]

  player = info[4:]
  player = re.split('(BLOCKED|,)', player, re.IGNORECASE)
  player = player[0]
  shot_info["player"] = player
  shot_info["team"] = team

  return shot_info

def parse_sog_info(details):
  shot_info = {}
  info = details.contents if len(details.contents) > 1 else details.text
  team = info[:3]

  player = info.split('-')
  player = player[1].split(',')
  player = player[0]
  shot_info["player"] = player
  shot_info["team"] = team

  return shot_info

# TO DO: what are the numbers listed after the player names & where should this data go?
def parse_goal_info(details):
  goal_info = {}
  info = details.contents if len(details.contents) > 1 else details.text
  team = info[:3]

  player = info[0][8:].split(',')
  player = player[0][0:-3]
  assists = re.split('[:;]', info[2], re.IGNORECASE)
  assists = assists[1:]
  for i, a in enumerate(assists):
    assists[i] = assists[i][0:-3]

  goal_info["team"] = team
  goal_info["assists"] = assists
  goal_info["player"] = player
  # shot_type,  shot_zone, shot_distance

  return goal_info

def parse_penalty_info(details):
  penalty_info = {}
  info = details.contents if len(details.contents) > 1 else details.text
  team = info[:3]

  penalty = info[4:]
  penalty_string = re.split('[,:]', penalty, re.IGNORECASE)
  player_and_penalty = penalty_string[0].split('&nbsp;')
  player = player_and_penalty[0]
  penalty = player_and_penalty[1]

  penalty_info["penalty"] = penalty
  penalty_info["called_on"] = { "player": player, "team": team}
  penalty_info["drawn_by"] = { "player": penalty_string[2][5:], "team": penalty_string[2][1:4] }
  penalty_info["zone"] = penalty_string[1][1:4]

  return penalty_info

def parse_possession_change(details):
  possession_info = {}
  info = details.contents if len(details.contents) > 1 else details.text
  team = info[:3]

  player = info.split('-')
  player = player[1].split(',')
  zone = player[1][1:4]
  player = player[0]
  possession_info["team"] = team
  possession_info["player"] = player
  possession_info["zone"] = zone

  return possession_info

def parse_faceoff_info(details):
  faceoff_info = {}
  # info = details.contents if len(details.contents) > 1 else details.text
  info = details.contents[0] if details.contents else None
  team = info[:3]
  zone = info.split('won ')
  zone = zone[1][:3]
  players = info.split('-')
  players = players[1].split(' vs ')

  faceoff_info["winning_team"] = team
  faceoff_info["zone"] = zone
  faceoff_info["players"] = [{ "team": players[0][1:4], "player": players[0][5:]}, { "team": players[1][:3], "player": players[1][4:]}]

  return faceoff_info
