# Get a list of URLs to scrape
# param => build_url: string, the url to build
# param => iterators: dict, url pieces that must be iterated over
# return => list: all urls that need to be scraped
def get_urls(build_url, iterators):

  seasons = iterators["seasons"]
  pages = iterators["pages"]

  urls = []

  for i, s in enumerate(seasons):
    for ind, page in enumerate(pages):
      url = build_url.format(str(s), str(page))
      urls.append(url)

  return urls



# Play-by-Plays: http://www.nhl.com/scores/htmlreports/{0}/PL0{1}.HTM
# TOI Reports: http://www.nhl.com/scores/htmlreports/{0}/T{1}.HTM
# Player Pages: http://www.nhl.com/ice/playersearch.htm? season={0}&pg={1}


# build_url = "http://www.nhl.com/ice/playersearch.htm?season={0}&pg={1}"
# iterators = { "seasons": [20112012, 20122013], "pages": range(1, 22) }
# get_urls(build_url, iterators)