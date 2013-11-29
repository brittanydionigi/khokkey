from BeautifulSoup import BeautifulSoup
import re
import requests

base_url = "http://www.nhl.com/scores/htmlreports/"
seasons = [20022003,20032004,20042005,20052006,20062007,20072008,20082009,20092010,20102011,20112012,20122013,20132014]
game_id = "20139"
urls = []

for i, s in enumerate(seasons):
  urls.append(base_url + "{0}/PL0{1}.HTM".format(str(s), game_id))


def get_game_info():
  #get teams, date, final score, home vs away, season, start time

def get_player_toi():
  #find out whos one the ice at what times/for how long

def get_game_events(events):
  game_events = []
  { "event_type": "SHOT", "team": "BOS", "period": 2, "player": "last name?unique id?lastname-number-team?", "strength": "EV", "time_elapsed": "00:24" }

  event_detail = {}
  game_events.append(event_detail)

  return game_events


  for i, e in enumerate(events):
    get the event type, from there branch off and see what specific scraping needs to be done for each subsequent td

    # PSTR = period start
    # FAC = faceoff
    # MISS
    # SHOT
    # HIT
    # BLOCK
    # STOP
    # GIVE = giveaway
    # PENL = penalty
    # GOAL
    # TAKE
    # PEND = period end
    # GEND = game end

# param stats: array An array of the stats we want to calculate (i.e. fenwick, corsi, etc)
def calculate_fenwick(shot_events):
  fenwick = { "fenwick": 0 , "fenwick_for": 0, "fenwick_against": 0, "fenwick_for_percentage": 0 }

  for s in shot_events:
      fenwick_stat = { s["team"}: }


  fenwick = { "bos": { "fenwick": 0, "fenwick_for": 0, "fenwick_against": 0, "fenwick_for_percentage": 0}, "sj": {"fenwick": 0, "fenwick_for": 0, "fenwick_against": 0, "fenwick_for_percentage": 0} }
  shot_data = game_data["sog"] + game_data["shots_missed"]
  for s in shot_data:
    if s["team"] == "BOS":
      fenwick["bos"]["fenwick"] += 1
      fenwick["bos"]["fenwick_for"] += 1
      fenwick["bos"]["fenwick_for_percentage"] = (100 * fenwick["bos"]["fenwick_for"]) / (fenwick["bos"]["fenwick_for"] + fenwick["bos"]["fenwick_against"])
      fenwick["sj"]["fenwick_against"] += 1
    if s["team"] == "S.J":
      fenwick["sj"]["fenwick"] += 1
      fenwick["sj"]["fenwick_for"] += 1
      fenwick["bos"]["fenwick_against"] += 1
      fenwick["sj"]["fenwick_for_percentage"] = (100 * fenwick["sj"]["fenwick_for"]) / (fenwick["sj"]["fenwick_for"] + fenwick["sj"]["fenwick_against"])
  return fenwick


  return fenwick

def calculate_corsi(shot_events):



def get_game_sog(url):
  r = requests.get(url)
  if r.status_code==200:
    soup = BeautifulSoup(r.content)

    game_logs = soup.findAll('table', { 'class': 'tablewidth'})
    shots = []

    for i, gl in enumerate(game_logs):
      rows = gl.findAll('tr', { 'class':'evenColor'})

      for i, r in enumerate(rows):
        shotevents = [el for el in r.findAll('td') if el.text == "SHOT"]

        for i, se in enumerate(shotevents):
            shot_dict = {}
            detail = se.findNextSibling('td').text
            team = detail[:3]
            player = detail.split('-')
            player = player[1].split(',')
            player = player[0]
            shot_dict["player"] = player
            shot_dict["team"] = team
            shots.append(shot_dict)

  return shots

def get_game_shots_missed(url):
  r = requests.get(url)
  if r.status_code==200:
    soup = BeautifulSoup(r.content)

    game_logs = soup.findAll('table')
    shots = []

    for i, gl in enumerate(game_logs):
      rows = gl.findAll('tr', { 'class':'evenColor'})

      for i, r in enumerate(rows):
        shotevents = [el for el in r.findAll('td') if el.text == "MISS"]

        for i, se in enumerate(shotevents):
            shot_dict = {}
            detail = se.findNextSibling('td').text
            team = detail[:3]
            player = detail[4:]
            player = player.split(',')
            player = player[0]
            shot_dict["player"] = player
            shot_dict["team"] = team
            shots.append(shot_dict)

  return shots

def get_game_shots_blocked(url):
  r = requests.get(url)
  if r.status_code==200:
    soup = BeautifulSoup(r.content)

    game_logs = soup.findAll('table')
    shots = []

    for i, gl in enumerate(game_logs):
      rows = gl.findAll('tr', { 'class':'evenColor'})

      for i, r in enumerate(rows):
        shotevents = [el for el in r.findAll('td') if el.text == "BLOCK"]

        for i, se in enumerate(shotevents):
            shot_dict = {}
            detail = se.findNextSibling('td').text
            team = detail[:3]
            player = detail[4:]
            player = player.split('BLOCKED')
            player = player[0]
            shot_dict["player"] = player
            shot_dict["team"] = team
            shots.append(shot_dict)

  return shots

def get_team_fenwick(game_data):
  fenwick = { "bos": { "fenwick": 0, "fenwick_for": 0, "fenwick_against": 0, "fenwick_for_percentage": 0}, "sj": {"fenwick": 0, "fenwick_for": 0, "fenwick_against": 0, "fenwick_for_percentage": 0} }
  shot_data = game_data["sog"] + game_data["shots_missed"]
  for s in shot_data:
    if s["team"] == "BOS":
      fenwick["bos"]["fenwick"] += 1
      fenwick["bos"]["fenwick_for"] += 1
      fenwick["bos"]["fenwick_for_percentage"] = (100 * fenwick["bos"]["fenwick_for"]) / (fenwick["bos"]["fenwick_for"] + fenwick["bos"]["fenwick_against"])
      fenwick["sj"]["fenwick_against"] += 1
    if s["team"] == "S.J":
      fenwick["sj"]["fenwick"] += 1
      fenwick["sj"]["fenwick_for"] += 1
      fenwick["bos"]["fenwick_against"] += 1
      fenwick["sj"]["fenwick_for_percentage"] = (100 * fenwick["sj"]["fenwick_for"]) / (fenwick["sj"]["fenwick_for"] + fenwick["sj"]["fenwick_against"])
  return fenwick


def get_team_corsi(game_data):
  corsi = { "bos": { "corsi": 0, "corsi_for": 0, "corsi_against": 0, "corsi_for_percentage": 0}, "sj": {"corsi": 0, "corsi_for": 0, "corsi_against": 0, "corsi_for_percentage": 0} }
  shot_data = game_data["sog"] + game_data["shots_missed"] + game_data["shots_blocked"]
  for s in shot_data:
    if s["team"] == "BOS":
      corsi["bos"]["corsi"] += 1
      corsi["bos"]["corsi_for"] += 1
      corsi["bos"]["corsi_for_percentage"] = (100 * corsi["bos"]["corsi_for"]) / (corsi["bos"]["corsi_for"] + corsi["bos"]["corsi_against"])
      corsi["sj"]["corsi_against"] += 1
    if s["team"] == "S.J":
      corsi["sj"]["corsi"] += 1
      corsi["sj"]["corsi_for"] += 1
      corsi["bos"]["corsi_against"] += 1
      corsi["sj"]["corsi_for_percentage"] = (100 * corsi["sj"]["corsi_for"]) / (corsi["sj"]["corsi_for"] + corsi["sj"]["corsi_against"])
  return corsi

if __name__ == '__main__':
  for u in urls:
    print u
    sog = get_game_sog(u)
    shots_missed = get_game_shots_missed(u)
    shots_blocked = get_game_shots_blocked(u)
    game_data = {}
    game_data["sog"] = []
    game_data["shots_missed"] = []
    game_data["shots_blocked"] = []

    for s in sog:
      game_data["sog"].append(s)
    for s in shots_missed:
      game_data["shots_missed"].append(s)
    for s in shots_blocked:
      game_data["shots_blocked"].append(s)

    game_data["corsi"] = get_team_corsi(game_data)
    game_data["fenwick"] = get_team_fenwick(game_data)
    print len(game_data["sog"])
    print len(game_data["shots_missed"])
    print len(game_data["shots_blocked"])
    print game_data["corsi"]
    print game_data["fenwick"]
