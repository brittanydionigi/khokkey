from BeautifulSoup import BeautifulSoup, Tag
import re
import requests
import itertools
import inspect




def iterate_stat_rows(stat_table, player):
  stats_rows = stat_table.findAll('tr', {'style': 'font-weight: bold;'})

  for i, stats_row in enumerate(stats_rows):
    stats_td_elems = stats_row.findAll('td')
    player_history = {}
    for i, stats_td_elem in enumerate(stats_td_elems):
      if i == 0:
        player_history["season"] = stats_td_elem.text
      if i == 1:
        player_history["team"] = stats_td_elem.text
    player["teams"].append(player_history)


def get_player_stats(player):
  player_url = "http://www.nhl.com/ice/player.htm?id=" + player["nhl_id"]
  print player_url
  rpu = requests.get(player_url)

  if rpu.status_code == 200:
    player_soup = BeautifulSoup(rpu.content)
    tombstone = player_soup.find('div', {'id': 'tombstone'})
    player_stats = player_soup.findAll('table', {'class': 'data playerStats'})
    sweater_number = tombstone.find('span', {'class': 'sweater'})
    if sweater_number:
      player["current_number"] = sweater_number.text
    else:
      player["current_number"] = None
    player["teams"] = []

    # Remove the last table in our player stats. It is the playoffs stats table, which is a reiteration
    # of the regular season table.
    playoff_stats = player_stats[-1]
    player_stats.pop(-1)

    for i, player_stats_table in enumerate(player_stats):
      iterate_stat_rows(player_stats_table, player)

    # If teams is empty after iterating the regular season table, let's check the playoff season table
    if len(player["teams"]) == 0:
      iterate_stat_rows(playoff_stats, player)

      # if it's STILL empty, the player never played in the NHL
      if len(player["teams"]) == 0:
        print "PLAYA NEVA PLAYED SON"
        print player
      # if we found some games, pop off the NHL Totals row at the end
      else:
        # Remove the last element in the player teams list. It is the NHL totals rows for stats
        player["teams"].pop(-1)

    # If they had regular season games, pop off the NHL Totals row at the end
    else:
      # Remove the last element in the player teams list. It is the NHL totals rows for stats
      player["teams"].pop(-1)



#NYR 24 CALLAHAN

#save nhl id of game players during initial scraping

#scrape the roster report for the game first => match up with IDs
#during each event do a lookup that maps the #24 CALLAHAN to an ID, save the player as an ID in each event