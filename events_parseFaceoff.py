# Standard Format: PHX won Def. Zone - CHI #19 TOEWS vs PHX #8 LOMBARDI
def faceoff(info):
  team = info[:3]
  players = info.split('Zone - ')
  players = players[1].split(' vs ')
  players = [parse_player(players[0]), parse_player(players[1])]

  return { "team": team, "players": players }

