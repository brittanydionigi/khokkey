
iterators = { "season": [], "pg": [] }
iterators = { "htmlreports/": [], "PL0": [] }


http://www.nhl.com/scores/htmlreports/20122013/PL020025.HTM



# Get URLs to scrape
# param => base_url: string, the base url to build off
# param => structure: string, where we want to format/replace the url with iterator data
# param => iterators: dict, url pieces that must be iterated over
# return => list: all urls that need to be scraped
def get_urls(base_url, structure, iterators):


  seasons = [20112012,20122013,20132014]
  player_pages = range(1, 22)

  urls = []

  for i, s in enumerate(seasons):
    for ind, player_page in enumerate(player_pages):
      url = base_url + "season={0}&pg={1}".format(str(s), str(player_page))
      urls.append(url)

  return urls