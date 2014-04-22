# Get a list of URLs to scrape
# param => period: integer, the period # we are in
# param => time_expired: string, the time expired in given period e.g. 18:54
# return => total_time_expired: integer, time (seconds) that have expired in the game
def get_total_time_expired(period, time_expired):

  # Fix for weird time elapsed on http://www.nhl.com/scores/htmlreports/20072008/PL020233.HTM
  if time_expired == "-16:0-1":
    time_expired = "0:00"

  game_clock = time_expired.split(':')
  minutes = int(game_clock[0]) + ((period - 1) * 20)
  seconds = int(game_clock[1])
  total_time_expired = str(minutes).zfill(2) + ":" + str(seconds).zfill(2)
  return total_time_expired