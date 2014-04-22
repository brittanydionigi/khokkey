# TO DOs:
    # where are the saves? are they the goalie stops?  (Shots on goal - goals), get which goalie is on the ice at the time and add/subtract from save %
    # calculate the final score?
    # what happens if both teams are away?
    # put game number and away/home game number in teams/season table
    # put goal/point tally in players table
    # players need to have unique IDs
    # TOI reports
    # when to calculate corsi/fenwick stats
    # check that EV, SH, and PP are the only strengths possible
    # don't add blocked_by to shot events where it's N/A?
    # seperate penalty minutes from penalty type (double (10 min)) in 20371 for 20132014

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

from bs4 import BeautifulSoup, Tag
import re
import requests
import itertools
import inspect
# import dataset
import pymongo

from strength import get_strength_transitions
from game_rosters import get_game_rosters
from util_getUrls import get_urls


from pymongo import MongoClient
client = MongoClient()

db = client['games']
games_table = db['games']

teamsdb = client['teams']
teams_table = teamsdb['teams']
# db.games.ensureIndex( { "season": 1, "gcode": 1 }, { unique: true, dropDups: true } )

#games_table = db['games']
#game_events_table = db['game_events']

base_url = "http://www.nhl.com/scores/htmlreports/"
seasons = [20122013]
#20022003,20032004,20042005,20052006,20062007,20072008,20082009,20092010,20102011,20112012,20122013,
# game_codes = range(20001, 20721)
game_codes = range(20025, 20026)
games = []

#Standard: 20371 [20132014]
#Shoot out example: 20610 [20132014]
#Overtime example: 20613 [20132014]
#Playoffs example: 30171 [20122013]
#Playoffs overtime example: 30213 [20112012]


# Iterate over seasons and game codes, building base game document
for i, s in enumerate(seasons):
  for ind, gid in enumerate(game_codes):
    game = { "season": s, "gcode": gid, "url": base_url + "{0}/PL0{1}.HTM".format(str(s), str(gid))}
    games.append(game)



temp_game_rosters = {}

def get_game_info(teams, info):
  game_meta = { "date": info.findAll('tr')[3].find('td').text }
  game_meta["score"] = []
  game_meta["team_abbrs"] = {};


  # SET PLAYOFFS DATA IF AVAILABLE
  playoff_series = info.findAll('tr')[2].find('td')
  if playoff_series.text and "Winter Classic" not in playoff_series.text:
    game_meta["playoffs"] = { "series": playoff_series.text }
  if playoff_series.text and "Winter Classic" in playoff_series.text:
    game_meta["series"] = playoff_series.text

  for t in teams:
    team_name = teams[t].findAll('tr')[-1].find('td').text

    # Montreal Canadien games have different formatting
    # This standardizes our split
    team_name = team_name.replace("Match/Game", "Game").split('Game')
    game_meta[t] = team_name[0].title()
    team_abbr = teams_table.find({ "team": game_meta[t] })
    team_abbr = team_abbr[0]["abbr"]
    game_meta["team_abbrs"][t] = team_abbr

    game_meta["score"].append({"team": game_meta[t], "score": 0 })
    if "playoffs" in game_meta:
      # TO DO: should only need to do this once, not twice for both teams
      game_meta["playoffs"]["game_number"] = team_name[1][1:2]


  temp_game_rosters.update(get_game_rosters(game_data["season"], game_data["gcode"], game_meta["away_team"], game_meta["home_team"]))

  return game_meta


def get_total_time_expired(period, time_expired):
  game_clock = time_expired.split(':')
  minutes = int(game_clock[0]) + ((period - 1) * 20)
  seconds = int(game_clock[1])
  total_time_expired = str(minutes).zfill(2) + ":" + str(seconds).zfill(2)
  return total_time_expired


def parse_event_info(event_type, details):

  def shot(info):
    #SHOT ON GOAL: T.B ONGOAL - #19 CROMBEEN, Backhand, Off. Zone, 37 ft.
    #MISS: T.B #8 BARBERIO, Slap, Wide of Net, Off. Zone, 52 ft.
    #BLOCK: T.B #2 BREWER BLOCKED BY PHI #8 GROSSMANN, Slap, Def. Zone


    #team = info[:3]
    info = info.split(', ')
    #player = info[0][4:]
    team_player = parse_player(info[0])

    blocked_by = None
    shot_distance = None
    missed_puck = None

    # If the shot type was BLOCK. Checking for # to see if another player is listed in the game info?
    if info[1].find('#') != -1:
      shot_type = info[2]
      blocked_by = parse_player(info[1][:3] + " " + info[1][4:])
    else:
      shot_type = info[1]
      shot_distance = info[-1].replace(" ft.","").strip(' \t\n\r')

    return { "team": team_player["team"], "player" : team_player["player"], "blocked_by": blocked_by, "shot_type": shot_type, "shot_distance": shot_distance }

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
    team_player = parse_player(team + " " + player)

    shot_type = goal_info[1]
    shot_distance = goal_info[-1].replace(" ft.","").strip(' \t\n\r')
    assists = []

    # If info is a list with 2 items in it, the second item is our assists information.
    # Otherwise, info is just a string and len will return the length of the goal info text.
    if len(info) == 2:
      assist_info = info[1].text.replace("Assists: ", "").split('; ')

      for i, a in enumerate(assist_info):
        assists.append(parse_player(team_player["team"] + " " + a[0:-3]))

    # Update Game Score
    full_team = teams_table.find({ "abbr": team })
    full_team = full_team[0]["team"]
    for i, t in enumerate(game_data["score"]):
      if t["team"] == full_team:
        t["score"] = t["score"] + 1

    return { "team": team_player["team"], "player": team_player["player"], "shot_type": shot_type, "shot_distance": shot_distance, "assists": assists }

  # TO DO: cleanup
  def penalty(info):
    split_patterns = [" ", "\\xa0"]
    join_pattern = "|".join(split_patterns)
    p = re.compile(join_pattern)
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


    # Grab the name of the penalty & minutes
    # Standard format is:  T.B #3 AULIE Roughing(2 min), Neu. Zone Drawn By: PHI #10 SCHENN
    penalty_type = penalty.split(',')[0] # => AULIE Roughing(2 min)

    # Sometimes there is no comma after the minutes. In this case, split at Drawn
    if " Drawn" in penalty_type:
      penalty_type = penalty_type.split(' Drawn')
      penalty_type = penalty_type[0]

    return { "penalty": penalty_type, "called_on": called_on, "drawn_by": drawn_by, "team": called_on["team"] }

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

  def hit(info):
    team = info[:3]
    info = info.split(' HIT ')
    whoGotHit = info[1].split(',')
    players = [parse_player(info[0]), parse_player(whoGotHit[0])]
    return { "team": team, "players": players }


  # Standard Format: PHX won Def. Zone - CHI #19 TOEWS vs PHX #8 LOMBARDI
  def faceoff(info):
    team = info[:3]
    players = info.split('Zone - ')
    players = players[1].split(' vs ')
    players = [parse_player(players[0]), parse_player(players[1])]

    return { "team": team, "players": players }



  events = {
    "SOG" : shot,
    "Missed" : shot,
    "Blocked" : shot,
    "GOAL": goal, # TO DO: get goalie on ice at the time
    "TAKE" : possession,
    "GIVE" : possession,
    "PENL" : penalty,
    "FAC" : faceoff,
    "HIT": hit
  }

  def replace_all(string, dict):
    for i, j in dict.iteritems():
      string = string.replace(i, j)
    return string



  event_info = {}
  info = details.contents if len(details.contents) > 1 else details.text

  # If info winds up being a string (why would it be contents?), replace
  # some substrings right off the bad for easier parsing of event details
  # Maybe for players on ice scenario??
  if isinstance(info, basestring):
    info = replace_all(info, { " BLOCKED BY ": ",", "TAKEAWAY - " : "", "GIVEAWAY - " : "", "ONGOAL - " : "", "&nbsp;" : " " })


  # # TO DO: map team names to abbreviations and un-hardcode this
  # if details.contents[0][:3] == 'NYR' or details.contents[0][:3] == 'WSH':
  #   event_info["team"] = details.contents[0][:3]

  # Remap zone names




  zone = details.contents[0].find('Zone')
  if zone != -1:
    remapped_zones = {
      "Neu": "Neutral",
      "Off": "Offensive",
      "Def": "Defensive"
    }
    event_info["zone"] = remapped_zones[details.contents[0][zone-5:zone-2]]







  # Try parsing event info; otherwise just return the object
  try:
    event_info.update(events[event_type](info))
    return event_info
  except KeyError:
    return event_info



def get_game_events(events, regular_season):
  game_events = []

  for i, e in enumerate(events):
    event_detail = { "period": e["period"] }
    event_row_data = e["event_row"].findAll('td')

    for ind, erd in enumerate(event_row_data):


      # 3rd TD Element => strength
      if ind == 2:

        if erd.text == "EV" or erd.text == "SH" or erd.text == "PP":
          event_detail["strength"] = erd.text



      # 4th TD Element => time expired / time remaining
      if ind == 3:
        game_clock = erd.contents
        event_detail["period_time_expired"] = game_clock[0].split(':')[0].zfill(2) + ":" + game_clock[0].split(':')[1].zfill(2)
        event_detail["total_time_expired"] = get_total_time_expired(e["period"], game_clock[0])
        if e["period"] >= 4:
          event_detail["period"] = "OT"
          how_many_ots = (e["period"] - 3)
          if how_many_ots > 1:
            event_detail["period"] = str(how_many_ots) + "OT"

        if e["period"] == 5 and regular_season == True:
          event_detail["period"] = "SO"




      # 5th TD Element => event type
      # 6th TD Element => event details/info/description
      if ind == 4:
        mapped_event_types = {
          "SHOT": "SOG",
          "MISS": "Missed",
          "BLOCK": "Blocked"
        }
        event_description = erd.findNextSibling('td')

        try:
          event_type = mapped_event_types[erd.text]
        except KeyError:
          event_type = erd.text

        event_detail["event_type"] = event_type
        event_detail.update(parse_event_info(event_type, event_description))


    game_events.append(event_detail)
    #game_events_table.insert(event_detail)
  return game_events



if __name__ == '__main__':
  for g in games:
    print g["url"]
    r = requests.get(g["url"])

    game_data = { "season": g["season"], "gcode": g["gcode"] }

    # If we can access the file, fill in the rest of the game data
    if r.status_code == 200:
      soup = BeautifulSoup(r.content)
      body = soup.find('body')
      game_tables = []
      game_rows = []

      # Store all the tables from the page in game_tables
      for item in body.contents:
        if type(item) is Tag and item.name == 'table':
          game_tables.append(item)



      teams = { "away_team": soup.find('table', { 'id': 'Visitor'}), "home_team": soup.find('table', { 'id': 'Home'}) }
      game_info = soup.find('table', { 'id': 'GameInfo' })
      game_data.update(get_game_info(teams, game_info))

      game_data["events"] = []
      if "playoffs" in game_data.keys():
        regular_season = False
      else:
        regular_season = True

      # Iterate over all game tables
      for i, gt in enumerate(game_tables):
        # Get all event rows
        event_rows = [el for el in gt.findAll('tr', { 'class':'evenColor'}) if el.text]
        for ind, e in enumerate(event_rows):
          game_rows.append({ "period": i + 1, "event_row": e })


      game_data["events"] = get_game_events(game_rows, regular_season)
      game_data["strength_transitions"] = get_strength_transitions(game_data["team_abbrs"], game_data["events"])

      # print game_data

      try:
        games_table.insert(game_data)
      except pymongo.errors.DuplicateKeyError:
        print "Duplicate Key, Skipping for now"
      except pymongo.errors.OperationFailure:
        print "fail"

    else:
      print "UNABLE TO REQUEST URL. STATUS CODE: " + str(r.status_code)