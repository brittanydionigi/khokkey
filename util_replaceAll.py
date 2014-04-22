def replace_all(string, dict):
  for i, j in dict.iteritems():
    string = string.replace(i, j)
  return string