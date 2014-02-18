# TO DOs:
    # where are the saves? are they the goalie stops?  (Shots on goal - goals), get which goalie is on the ice at the time and add/subtract from save %
    # calculate the final score?
    # what happens if both teams are away?
    # put game number and away/home game number in teams/season table
    # put goal/point tally in players table
    # players need to have unique IDs
    # TOI reports
    # when to calculate corsi/fenwick stats

# Events:
    # HIT
    # SOC = shootout complete
    # PSTR = period start --
    # STOP --
    # PEND = period end --
    # GEND = game end --

    # FAC = faceoff *
    # GOAL *
    # TAKE *
    # GIVE = giveaway *
    # BLOCK *
    # MISS *
    # SHOT *
    # PENL = penalty *

    # -- Does not follow rules for 'team'

from BeautifulSoup import BeautifulSoup, Tag
import re
import requests
import itertools
import inspect
import dataset

#box648.bluehost.com
#box796.bluehost.com
#50.87.139.53
#host all all 50.87.139.53 50.87.139.53 trust
#host all all 69.195.126.101 69.195.126.101 trust
#host all all 66.147.244.01 66.147.244.99 trust

#db = dataset.connect('postgresql://shortsof_admin:Ny24CnE86a8He@50.87.139.53:5432/shortsof_khokkey')
#db = dataset.connect('mysql://shortsof_admin:Ny24CnE86a8He@box648.bluehost.com:3306/shortsof_khokkey')
#games_table = db['games']

base_url = "http://www.nhl.com/scores/htmlreports/"
seasons = [20082009,20092010,20102011,20112012]
#20022003,20032004,20042005,20052006,20062007,20072008,20082009,20092010,20102011,20112012,20122013

#20122013: 20720
#20112012: 21230
#20102011: 21230
#20092010: 21230


game_ids= range(20001, 21230)
games = []

for i, s in enumerate(seasons):
  season = s
  for e, gcode in enumerate(game_ids):
    game = { "season": season, "gcode": gcode, "url": base_url + "{0}/PL0{1}.HTM".format(str(season), gcode) }
    games.append(game)

def get_game_info(season, gcode, teams, info):
  game_meta = { "season": season, "gcode": gcode, "date": info.findAll('tr')[3].find('td').text }

  if info.findAll('tr')[2].find('td').text:
    game_meta["playoffs"] = { "series": info.findAll('tr')[2].find('td').text }

  for t in teams:
    team_name = teams[t].findAll('tr')[-1].find('td').text
    team_name = team_name.split('Game')
    game_meta[t] = team_name[0]
    if "playoffs" in game_meta:
      # TO DO: should only need to do this once, not twice for both teams
      game_meta["playoffs"]["game_number"] = team_name[1][1:2]

  return game_meta


def get_total_time_expired(period, time_expired):
  game_clock = time_expired.split(':')
  minutes = int(game_clock[0]) + ((period - 1) * 20)
  seconds = int(game_clock[1])
  total_time_expired = str(minutes).zfill(2) + ":" + str(seconds).zfill(2)
  return total_time_expired


def parse_event_info(event_type, details):

  def shot(info):
    info = info.split(', ')
    player = info[0][4:]
    blocked_by = None
    shot_distance = None
    if info[1].find('#') != -1:
      shot_type = info[2]
      blocked_by = { "team": info[1][:3], "player": info[1][4:] }
    else:
      shot_type = info[1]
      shot_distance = info[3][:3]

    return { "player" : player, "blocked_by": blocked_by, "shot_type": shot_type, "shot_distance": shot_distance }

  def possession(info):
    info = info.split(', ')
    return parse_player(info[0])

  def goal(info):
    if isinstance(info, basestring):
      goal_info = info.split(', ')
    else:
      goal_info = info[0].split(', ')

    team = goal_info[0][:3]
    player = goal_info[0].split('(')
    player = player[0][4:]
    shot_type = goal_info[1]
    shot_distance = goal_info[3]

    assists = re.split('[:;]', info[2])
    assists = assists[1:]
    for i, a in enumerate(assists):
      assists[i] = assists[i][0:-3]

    return { "team": team, "player": player, "shot_type": shot_type, "shot_distance": shot_distance, "assists": assists }

  # TO DO: cleanup
  def penalty(info):
    p = re.compile(" ")
    for i, m in enumerate(p.finditer(info)):
        if i == 2:
          split_end = m.end()
          split_start = m.start()

    player = info[:split_start]
    penalty = info[split_end:]

    called_on = parse_player(player)
    drawn_by = "N/A"
    if "Drawn By:" in penalty:
      drawn_by = parse_player(penalty.split(': ')[1])

    penalty = penalty.split(',')[0]

    return { "penalty": penalty, "called_on": called_on, "drawn_by": drawn_by }

  def parse_player(team_player):
    player = team_player[4:]
    team = team_player[:3]
    return { "team": team, "player": player}

  # TO DO: cleanup
  def faceoff(info):
    # TO DO: splitting on a hyphen might be dangerous if someone's last name contains one
    players = info.split('- ')
    players = players[1].split(' vs ')
    players = [parse_player(players[0]), parse_player(players[1])]
    return { "players": players }

  def noop(info):
    return {}

  events = {
    "SHOT" : shot,
    "MISS" : shot,
    "BLOCK" : shot,
    "GOAL": goal, # TO DO: get goalie on ice at the time
    "TAKE" : possession,
    "GIVE" : possession,
    "PENL" : penalty,
    "FAC" : faceoff,
    "PSTR": noop,
    "PEND": noop,
    "GEND": noop,
    "HIT": noop,
    "STOP": noop,
    "SOC": noop
  }

  def replace_all(string, dict):
    for i, j in dict.iteritems():
      string = string.replace(i, j)
    return string



  event_info = {}
  info = details.contents if len(details.contents) > 1 else details.text

  # TO DO: map team names to abbreviations and un-hardcode this
  if details.contents[0][:3] == 'NYR' or details.contents[0][:3] == 'WSH':
    event_info["team"] = details.contents[0][:3]

  zone = details.contents[0].find('Zone')
  if zone != -1:
    event_info["zone"] = details.contents[0][zone-5:zone-2]

  if isinstance(info, basestring):
    info = replace_all(info, { " BLOCKED BY ": ",", "TAKEAWAY - " : "", "GIVEAWAY - " : "", "ONGOAL - " : "", "&nbsp;" : " " })

  event_info.update(events[event_type](info))
  #print event_info
  return event_info



def get_players(events, away_team, home_team):
  players = []

  for i, e in enumerate(events):
    event_row_data = e["event_row"].findAll('td')

    for ind, erd in enumerate(event_row_data):

      if ind == 6 or 7:
        font_tags = [el for el in erd.findAll('font')]
        for i, f in enumerate(font_tags):
          player_info = f["title"].split(' - ')
          player_name = player_info[1].split(' ')
          player_number = f.text
          player_info = { "position": player_info[0], "number": player_number, "first_name": player_name[0], "last_name": player_name[1] }
          # if ind == 6:
          #   team = { "team": away_team }
          # if ind == 7:
          #   team = { "team": home_team }
          # player_info.update(team)
          if player_info not in players:
            players.append(player_info)

  #sortedplayers = sorted(players, key=lambda k: k['last_name'])
  #for i, player in enumerate(sortedplayers):
    #print player["number"], player["last_name"], player["first_name"]

  return players



if __name__ == '__main__':
  nhl_players = []
  for g in games:
    print g["url"]

    r = requests.get(g["url"])
    if r.status_code==200:
      game_data = {}
      soup = BeautifulSoup(r.content)

      body = soup.find('body')
      game_tables = []
      game_rows = []

      for item in body.contents:
        if type(item) is Tag and item.name == 'table':
          game_tables.append(item)



      teams = { "away_team": soup.find('table', { 'id': 'Visitor'}), "home_team": soup.find('table', { 'id': 'Home'}) }
      game_info = soup.find('table', { 'id': 'GameInfo' })
      game_data = get_game_info(g["season"], g["gcode"], teams, game_info)
      game_data["players"] = []


      #iterate over all tables
      for i, gt in enumerate(game_tables):
        event_rows = [el for el in gt.findAll('tr', { 'class':'evenColor'}) if el.text]
        for ind, e in enumerate(event_rows):
          game_rows.append({ "period": i + 1, "event_row": e })

    game_data["players"] = get_players(game_rows, game_data["away_team"], game_data["home_team"])
    nhl_players.append(game_data["players"])


  sortedplayers = sorted(nhl_players, key=lambda k: k['last_name'])
  for i, player in enumerate(sortedplayers):
    print player["last_name"], player["first_name"], player["number"]

    #print game_data["players"]
    #print game_data["players"]
    #games_table.insert(game_data)
