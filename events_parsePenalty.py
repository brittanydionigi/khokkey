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
