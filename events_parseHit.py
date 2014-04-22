def hit(info):
  team = info[:3]
  info = info.split(' HIT ')
  whoGotHit = info[1].split(',')
  players = [parse_player(info[0]), parse_player(whoGotHit[0])]
  return { "team": team, "players": players }