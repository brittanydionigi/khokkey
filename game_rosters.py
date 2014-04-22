from BeautifulSoup import BeautifulSoup, Tag
import re
import requests
import itertools
import inspect
import pymongo
import logging



logging.basicConfig(format='%(levelname)s: %(message)s', filename='player_lookup.log',level=logging.DEBUG)

from pymongo import MongoClient
client = MongoClient()

db = client['players']

players_table = db['players']


def get_full_player_data(player, player_from_db, count):
  logging.info("\n")
  if count == 0:
    # logging.warning("COULDNT FIND PLAYER BY LAST NAME: " + player["last_name"])
    return player
  if count == 1:
    # logging.info("Found player by LAST name.")
    returned_player = player_from_db[0]
    player_full = { "number": player["number"], "nhl_id": returned_player["nhl_id"], "first_name": returned_player["first"], "last_name": returned_player["last"] }
    return player_full
  if count > 1:
    narrow_players_from_db = players_table.find({ "last_upper": player["last_name"], "first_upper": player["first_name"] })
    if narrow_players_from_db.count() == 0:
      # logging.warning("COULDNT FIND PLAYER BY FIRST AND LAST NAME: " + player["first_name"] + " " + player["last_name"])
      return player
    if narrow_players_from_db.count() == 1:
      logging.info("Found player by FIRST & LAST name.")
      returned_player = narrow_players_from_db[0]
      player_full = { "number": player["number"], "nhl_id": returned_player["nhl_id"], "first_name": returned_player["first"], "last_name": returned_player["last"] }
      return player_full
    if narrow_players_from_db.count() > 1:
      logging.info("Multiple Results (" + str(narrow_players_from_db.count()) + "). Narrowing by FIRST, LAST & POSITION... ")
      first_last_position = players_table.find({ "last_upper": player["last_name"], "first_upper": player["first_name"], "position": player["position"] })
      if first_last_position.count() == 0:
        # logging.warning("COULDNT FIND PLAYER BY FIRST, LAST & POSITION: " + player["first_name"] + " " + player["last_name"] + " " + player["position"])
        return player
      if first_last_position.count() == 1:
        logging.info("Found player by FIRST, LAST & POSITION.")
        returned_player = first_last_position[0]
        player_full = { "number": player["number"], "nhl_id": returned_player["nhl_id"], "first_name": returned_player["first"], "last_name": returned_player["last"] }
        return player_full
      if first_last_position.count() > 1:
        logging.warning("ERROR: MULTIPLE RESULTS => NEEDS FURTHER NARROWING. Narrowing results by FIRST, LAST & POSITION didn't work: " + player["first_name"] + " " + player["last_name"] + " " + player["position"])


def iterate_roster_rows(rows):
  team_roster = []
  rows.pop(0)
  for i, row in enumerate(rows):
    player = {}
    player_datas = row.findAll('td')
    for i, td_elem in enumerate(player_datas):
      if i == 0:
        player["number"] = td_elem.text
      if i == 1:
        player["position"] = td_elem.text
      if i == 2:
        player_name = td_elem.text.replace("  (A)", "").replace("  (C)", "")
        player_name = player_name.split(' ', 1)
        player["first_name"] = player_name[0]
        player["last_name"] = player_name[1]

    player_from_db = players_table.find({ "last_upper": player["last_name"] })
    players_returned = player_from_db.count()

    full_player_data = get_full_player_data(player, player_from_db, players_returned)
    team_roster.append(full_player_data)

  return team_roster



def get_game_rosters(game_data):
  season = game_data["season"]
  gcode = game_data["gcode"]
  away_team = game_data["away_team"]
  home_team = game_data["home_team"]

  roster_url = "http://www.nhl.com/scores/htmlreports/" + str(season) + "/RO0" + str(gcode) + ".HTM"
  rpu = requests.get(roster_url)

  if rpu.status_code == 200:
    roster_soup = BeautifulSoup(rpu.content)
    roster_table = roster_soup.find('table', {'class': 'tablewidth'})
    roster_table = roster_table.find('table', {'class': 'tablewidth'})
    roster_table_rows = roster_table.findAll('tr', recursive=False)
    roster_table_rows = roster_table_rows[3].find('table')

    roster_table_rows = roster_table_rows.find('tr').findAll('td', recursive=False)

    visitor_rows = roster_table_rows[0].find('table')
    visitor_rows = visitor_rows.findAll('tr')

    home_rows = roster_table_rows[1].find('table')
    home_rows = home_rows.findAll('tr')


    visitor_roster = iterate_roster_rows(visitor_rows)
    home_roster = iterate_roster_rows(home_rows)


    return { "visitor_roster": visitor_roster, "home_roster": home_roster }