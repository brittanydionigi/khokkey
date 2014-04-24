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
import pymongo
import logging

requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

logging.basicConfig(format='%(levelname)s: %(message)s', filename='playbyplay.log',level=logging.DEBUG)


from strength import get_strength_transitions
from game_rosters import get_game_rosters
from util_getUrls import get_urls
from util_getTotalTimeExpired import get_total_time_expired
from util_replaceAll import replace_all
from util_dbInsert import db_insert

from events_getGameInfo import get_game_info


from pymongo import MongoClient
client = MongoClient()

db = client['games']
games_table = db['games']
# db.games.ensureIndex( { "season": 1, "gcode": 1 }, { unique: true, dropDups: true } )

teamsdb = client['teams']
teams_table = teamsdb['teams']

seasons = [20072008, 20082009, 20092010, 20102011, 20112012, 20122013, 20132014]
game_codes = range(20001, 21230)

games = []

# Iterate over seasons and game codes, building base game document
for i, season in enumerate(seasons):
  for ind, game_code in enumerate(game_codes):
    game = { "season": season, "gcode": game_code, "url": "http://www.nhl.com/scores/htmlreports/{0}/PL0{1}.HTM".format(str(season), str(game_code))}
    games.append(game)




def get_players_on_ice(team, tdelem):
  players_on_ice = []
  player_elems = [el for el in tdelem.findAll('font') if el.text]
  for playerindex, playername in enumerate(player_elems):
    players_on_ice.append(playername['title'])

  return players_on_ice


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






def parse_event_info(event_type, details):


  # SHOT ON GOAL: T.B ONGOAL - #19 CROMBEEN, Backhand, Off. Zone, 37 ft.
  # MISS: T.B #8 BARBERIO, Slap, Wide of Net, Off. Zone, 52 ft.
  # BLOCK: T.B #2 BREWER BLOCKED BY PHI #8 GROSSMANN, Slap, Def. Zone
  def shot(info):

    info = info.split(', ')
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





  # Original Format: CBJ #11 CALVERT Holding the stick(2 min), Neu. Zone Drawn By: DET #40 ZETTERBERG
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

    called_on = parse_player(player) # Parsing CBJ #11 CALVERT
    drawn_by = "N/A"
    if "Drawn By:" in penalty:
      drawn_by = parse_player(penalty.split(': ')[1]) # Parsing DET #40 ZETTERBERG


    # Grab the name of the penalty & minutes
    # Standard Format:  T.B #3 AULIE Roughing(2 min), Neu. Zone Drawn By: PHI #10 SCHENN
    penalty_type = penalty.split(',')[0] # => AULIE Roughing(2 min)

    # Sometimes there is no comma after the minutes. In this case, split at Drawn
    if " Drawn" in penalty_type:
      penalty_type = penalty_type.split(' Drawn')
      penalty_type = penalty_type[0]

    return { "penalty": penalty_type, "called_on": called_on, "drawn_by": drawn_by, "team": called_on["team"] }




  # Original Format: CBJ GIVEAWAY - #17 DUBINSKY, Def. Zone
  # Parsed Format: CBJ #17 DUBINSKY, Def. Zone
  def possession(info):
    info = info.split(', ')
    return parse_player(info[0])


  # Original Format: CBJ #17 DUBINSKY HIT DET #23 LASHOFF, Def. Zone
  def hit(info):
    team = info[:3]
    info = info.split(' HIT ')
    whoGotHit = info[1].split(',')
    players = [parse_player(info[0]), parse_player(whoGotHit[0])]
    return { "team": team, "players": players }


  # Original Format: PHX won Def. Zone - CHI #19 TOEWS vs PHX #8 LOMBARDI
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


  # Set the zone of the event if applicable
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
    event_row_data = e["event_row"].findAll('td', { "class": [" + bborder", " + bborder + rborder"] })

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

        # Set the event type and parse the event info
        event_detail["event_type"] = event_type
        event_detail.update(parse_event_info(event_type, event_description))




      # 6th & 7th TD Elements => players on ice
      if ind == 6:
        event_detail["away_players"] = get_players_on_ice("away", erd)

      if ind == 7:
        event_detail["home_players"] = get_players_on_ice("home", erd)



    game_events.append(event_detail)
  return game_events





if __name__ == '__main__':

  # Iterate over all of our games and start building up the metadata & events data
  for g in games:
    print g["url"]
    r = requests.get(g["url"])

    game_data = g

    game_in_table = games_table.find({ "gcode": g["gcode"], "season": g["season"] })
    try:
      if game_in_table[0]:
        print "Game in DB, continuing..."
        continue
    except IndexError:
      print "Not in db..."
      pass


    # If we can access the file, fill in the rest of the game data
    if r.status_code == 200:
      soup = BeautifulSoup(r.content)
      body = soup.find('body')
      game_tables = []
      game_rows = []


      # Store all the tables from the page in game_tables
      try:
        for item in body.contents:
          if type(item) is Tag and item.name == 'table':
            game_tables.append(item)
      except AttributeError:
        logging.error("Body returned as NoneType for " + g["url"])
        continue


      # Get additional game info (date, teams, etc.)
      teams = { "away_team": soup.find('table', { 'id': 'Visitor'}), "home_team": soup.find('table', { 'id': 'Home'}) }
      game_info = soup.find('table', { 'id': 'GameInfo' })
      game_data.update(get_game_info(teams, game_info))
      temp_game_rosters = get_game_rosters(game_data)



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


      # Insert new games into database
      db_insert(games_table, game_data)


    # Catch URLs that could not be requested
    else:
      print "UNABLE TO REQUEST URL. STATUS CODE: " + str(r.status_code)
