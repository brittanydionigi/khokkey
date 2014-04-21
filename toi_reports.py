from BeautifulSoup import BeautifulSoup, Tag
import re
import requests
import itertools
import inspect



toi_reports = ["http://www.nhl.com/scores/htmlreports/20132014/TV021120.HTM"]



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
        # print "Player Already Exists: " + this["last"]
        return True
        break
    # if player is new, return FALSE
    return False

if __name__ == '__main__':
  players = []
  for toi_report in toi_reports:
    # print roster_url
    r = requests.get(toi_report)

    # If we can access the file, grab player data per page
    if r.status_code == 200:
      soup = BeautifulSoup(r.content)
      body = soup.find('div', { 'class': 'pageBreakAfter' })
      team_headers = body.find('td', { 'class': 'teamHeading + border'}).text
      player_headers = [el for el in body.findAll('td', { 'class': 'playerHeading + border'})]
      # print player_headers
      # shift_rows = player_headers[0].parent.siblings.findAll('tr')
      # print shift_rows
      # print team_headers
      # use nextSibling to get each tr, if it doesnt have an odd/even class, mark it as overall stats, then start a new array for the next player

      team_shifts = {}

      for player in player_headers:
        team_shifts[player.text] = []


      parentrows = player_headers[0].parent.parent
      shift_rows = [el for el in parentrows.findAll('tr')]
      current_player_shifts = None
      for shifts in shift_rows:
        # print shifts.get('class')
        if shifts.find('td', { 'class': 'playerHeading + border'}):
          player = shifts.find('td', { 'class': 'playerHeading + border'}).text
          current_player_shifts = team_shifts[player]
        else:
          cells = shifts.findAll('td')
          if len(cells) == 6:
            if cells[0].text == "Shift #":
              continue
            else:
              shift = {
                'shift'         : cells[0].text,
                'period'        : 4 if cells[1].text == 'OT' else cells[1].text,
                'start_elapsed' : cells[2].text.split('/')[0].strip(),
                'start_game'    : cells[2].text.split('/')[1].strip(),
                'end_elapsed'   : cells[3].text.split('/')[0].strip(),
                'end_game'      : cells[3].text.split('/')[1].strip(),
                'duration'      : cells[4].text,
                'event'         : None if len(cells[5].text.strip()) == 0 else cells[5].text.strip()
              }
              current_player_shifts.append(shift)
          # else:
          #   if len(cells) == 7:
          #     if cells[0].text == "Per" or cells[0].text == "TOT":
          #       continue
          #     else:
          #       averages = {
          #         'period'        : 4 if cells[0].text == 'OT' else cells[0].text,
          #         'shift_count'   : cells[1].text,
          #         'shift_len_avg' : cells[2].text,
          #         'period_toi'    : cells[3].text,
          #         'even_strength' : cells[4].text,
          #         'pp_strength'   : cells[5].text,
          #         'sh_strength'   : cells[6].text
          #       }
          #       current_player_shifts.append(averages)
        # if it has a playerHeader class, start a new list
        # else, append to the current one

      print len(team_shifts['23 BROWN, J.T.'])

