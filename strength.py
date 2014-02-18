def parseGameTime(timeElapsed):
  time_expired = timeElapsed.split(':')
  minutes = int(time_expired[0]) * 60
  seconds = int(time_expired[1])
  time_expired = int(minutes + seconds)
  return time_expired;

def get_strength_transitions(teams, events):
  strength = [{"start_time": 0, "advantage": "EV" }]
  originalAdvantage = "EV"
  game_end = None

  # Iterate over game events
  for ind, event in enumerate(events):

    # If the event type is Game End, set the game_end to our total time expired value
    if event["event_type"] == "GEND":
      game_end = event["total_time_expired"]

    # If we have a strength value in our event object, and it's not empty
    if "strength" in event.keys() and len(event["strength"]) == 2:

      # Get the total time expired at the time of this event
      timeExpired = parseGameTime(event["total_time_expired"])
      eventStrength = event["strength"], # Set the current strength
      teamAdvantage = "EV" # Set a None advantage until we figure out who has it

      # If strenght is SHORT HANDED
      if event["strength"] == "SH":

        # And the event is a BLOCK
        if event["event_type"] == "BLOCK" or event["event_type"] == "Blocked":
          teamAdvantage = event["team"] # the advantage goes to the team in the event detail TD
        # If it's NOT a block
        else:
          if event["team"] == teams["away_team"]: # And the current event belongs to the AWAY TEAM
            teamAdvantage = teams["home_team"] # set the advantage to the HOME TEAM
          else:
            teamAdvantage = teams["away_team"]

      if event["strength"] == "PP":
        if event["event_type"] == "BLOCK" or event["event_type"] == "Blocked":
          if event["team"] == teams["away_team"]:
            teamAdvantage = teams["home_team"]
          else:
            teamAdvantage = teams["away_team"]
        else:
          teamAdvantage = event["team"]


      if originalAdvantage != teamAdvantage:
        originalAdvantage = teamAdvantage
        startTime = timeExpired

        strength[-1].update({"end_time": startTime })

        newStrengthFrame = { "start_time": startTime, "advantage": teamAdvantage }
        if teamAdvantage == teams["away_team"]:
          newStrengthFrame.update({"team_type": "away"})
        if teamAdvantage == teams["home_team"]:
          newStrengthFrame.update({"team_type": "home"})

        strength.append(newStrengthFrame)

  strength[-1].update({"end_time": parseGameTime(game_end) })

  return strength