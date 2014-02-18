from BeautifulSoup import BeautifulSoup, Tag
import re
import requests
import itertools
import inspect
import pymongo
from player_stats import get_player_stats

from pymongo import MongoClient
client = MongoClient()

db = client['players']

players_db = db['players']


base_url = "http://www.nhl.com/ice/playersearch.htm?"
seasons = [20112012,20122013,20132014]
player_pages = range(1, 22)

nhl_rosters = []

for i, s in enumerate(seasons):
  for ind, player_page in enumerate(player_pages):
    url = base_url + "season={0}&pg={1}".format(str(s), str(player_page))
    nhl_rosters.append(url)


def compare_keyVals(keyVals, obj):
  for key, val in keyVals.iteritems():
    # if the new player is not a perfect match to an existing player, return TRUE
    if obj[key] != val:
      return True
      break

  # if the new player already exists, return FALSE
  return False


def in_dictlist(keyVals, my_dictlist):
    for this in my_dictlist:
      player_is_new = compare_keyVals(keyVals, this)
      # if player is NOT new, return true
      if player_is_new == False:
        print "Player Already Exists: " + this["last"]
        return True
        break
    # if player is new, return FALSE
    return False

if __name__ == '__main__':
  players = []
  for roster_url in nhl_rosters:
    print roster_url
    r = requests.get(roster_url)

    # If we can access the file, grab player data per page
    if r.status_code == 200:
      soup = BeautifulSoup(r.content)
      body = soup.find('div', { 'id': 'pageBody' })
      players_table = body.find('table', { 'class': 'data playerSearch'})
      player_rows = [el for el in players_table.findAll('tr')]



      for i, player_row in enumerate(player_rows):
        player = {}
        datums = [el for el in player_row.findAll('td')]
        for i, datum in enumerate(datums):
          if i == 0:
            player["position"] = datum.text[-2:-1]
            player_name = datum.text.split(', ')
            player["last"] = player_name[0]
            player["first"] = player_name[1][:-4]
            player["last_upper"] = player_name[0].upper()
            player["first_upper"] = player_name[1][:-4].upper()
            nhl_url = datum.find('a')
            nhl_url = nhl_url["href"].split("?id=")
            nhl_id = nhl_url[1]
            player["nhl_id"] = nhl_id

          if i == 2:
            mapped_months = {
              "Jan": "01",
              "Feb": "02",
              "Mar": "03",
              "Apr": "04",
              "May": "05",
              "Jun": "06",
              "Jul": "07",
              "Aug": "08",
              "Sep": "09",
              "Oct": "10",
              "Nov": "11",
              "Dec": "12"
            }

            dob = datum.text.split(" ")
            month = mapped_months[dob[0]]
            year = dob[2]

            date_of_month = dob[1][:-1].zfill(2)

            player["dob"] = month + date_of_month + year

          if i == 3:
            player["hometown"] = datum.text


            if len(players) == 0:
              print "NO players, appending first one"
              players.append(player)
            else:
              player_exists = in_dictlist({"first": player["first"], "last": player["last"], "position": player["position"], "dob": player["dob"], "hometown": player["hometown"]}, players)

              if player_exists == False:
                get_player_stats(player)
                players.append(player)
                # print player
                players_db.insert(player)
              else:
                "Player " + player["first"] + " " + player["last"] + " already exists"




# print players


  # for player in players:
  #   players_table.insert(player)