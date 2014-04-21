from bs4 import BeautifulSoup, Tag
#import re
#import requests
#import itertools
#import inspect
import pymongo


# Database setup
from pymongo import MongoClient
client = MongoClient()

db = client['teams']
teams_table = db['teams']


# Teams dictionary
teams = [
  { "team": "Carolina Hurricanes", "slug": "carolina-panthers", "abbr": "CAR", "location": "Carolina", "mascot": "Hurricanes", "conference": "Eastern", "division": "Metropolitan" },
  { "team": "Columbus Blue Jackets", "slug": "columbus-blue-jackets", "abbr": "CBJ", "location": "Columbus", "mascot": "Blue Jackets", "conference": "Eastern", "division": "Metropolitan" },
  { "team": "New Jersey Devils", "slug": "new-jersey-devils", "abbr": "N.J", "location": "New Jersey", "mascot": "Devils", "conference": "Eastern", "division": "Metropolitan" },
  { "team": "New York Islanders", "slug": "new-york-islanders", "abbr": "NYI", "location": "New York", "mascot": "Islanders", "conference": "Eastern", "division": "Metropolitan" },
  { "team": "New York Rangers", "slug": "new-york-rangers", "abbr": "NYR", "location": "New York", "mascot": "Rangers", "conference": "Eastern", "division": "Metropolitan" },
  { "team": "Philadelphia Flyers", "slug": "philadelphia-flyers", "abbr": "PHI", "location": "Philadelphia", "mascot": "Flyers", "conference": "Eastern", "division": "Metropolitan" },
  { "team": "Pittsburgh Penguins", "slug": "pittsburgh-penguins", "abbr": "PIT", "location": "Pittsburgh", "mascot": "Penguins", "conference": "Eastern", "division": "Metropolitan" },
  { "team": "Washington Capitals", "slug": "washington-capitals", "abbr": "WSH", "location": "Washington", "mascot": "Capitals", "conference": "Eastern", "division": "Metropolitan" },
  { "team": "Boston Bruins", "slug": "boston-bruins", "abbr": "BOS", "location": "Boston", "mascot": "Bruins", "conference": "Eastern", "division": "Atlantic" },
  { "team": "Buffalo Sabres", "slug": "buffalo-sabres", "abbr": "BUF", "location": "Buffalo", "mascot": "Sabres", "conference": "Eastern", "division": "Atlantic" },
  { "team": "Detroit Red Wings", "slug": "detroit-red-wings", "abbr": "DET", "location": "Detroit", "mascot": "Red Wings", "conference": "Eastern", "division": "Atlantic" },
  { "team": "Florida Panthers", "slug": "florida-panthers", "abbr": "FLA", "location": "Florida", "mascot": "Panthers", "conference": "Eastern", "division": "Atlantic" },
  { "team": "Montreal Canadiens", "slug": "montreal-canandiens", "abbr": "MTL", "location": "Montreal", "mascot": "Canadiens", "conference": "Eastern", "division": "Atlantic" },
  { "team": "Ottawa Senators", "slug": "ottawa-senators", "abbr": "OTT", "location": "Ottawa", "mascot": "Senators", "conference": "Eastern", "division": "Atlantic" },
  { "team": "Tampa Bay Lightning", "slug": "tampa-bay-lightning", "abbr": "T.B", "location": "Tampa Bay", "mascot": "Lightning", "conference": "Eastern", "division": "Atlantic" },
  { "team": "Toronto Maple Leafs", "slug": "toronto-maple-leafs", "abbr": "TOR", "location": "Toronto", "mascot": "Maple Leafs", "conference": "Eastern", "division": "Atlantic" },
  { "team": "Chicago Blackhawks", "slug": "chicago-blackhawks", "abbr": "CHI", "location": "Chicago", "mascot": "Blackhawks", "conference": "Western", "division": "Central" },
  { "team": "Colorado Avalanche", "slug": "colorado-avalanche", "abbr": "COL", "location": "Colorado", "mascot": "Avalanche", "conference": "Western", "division": "Central" },
  { "team": "Dallas Stars", "slug": "dallas-stars", "abbr": "DAL", "location": "Dallas", "mascot": "Stars", "conference": "Western", "division": "Central" },
  { "team": "Minnesota Wild", "slug": "minnesota-wild", "abbr": "MIN", "location": "Minnesota", "mascot": "Wild", "conference": "Western", "division": "Central" },
  { "team": "Nashville Predators", "slug": "nashville-predators", "abbr": "NSH", "location": "Nashville", "mascot": "Predators", "conference": "Western", "division": "Central" },
  { "team": "St. Louis Blues", "slug": "st-louis-blues", "abbr": "STL", "location": "St. Louis", "mascot": "Blues", "conference": "Western", "division": "Central" },
  { "team": "Winnipeg Jets", "slug": "winnipeg-jets", "abbr": "WPG", "location": "Winnipeg", "mascot": "Jets", "conference": "Western", "division": "Central" },
  { "team": "Anaheim Ducks", "slug": "anaheim-ducks", "abbr": "ANA", "location": "Anaheim", "mascot": "Ducks", "conference": "Western", "division": "Pacific" },
  { "team": "Calgary Flames", "slug": "calgary-flames", "abbr": "CGY", "location": "Calgary", "mascot": "Flames", "conference": "Western", "division": "Pacific" },
  { "team": "Edmonton Oilers", "slug": "edmonton-oilers", "abbr": "EDM", "location": "Edmonton", "mascot": "Oilers", "conference": "Western", "division": "Pacific" },
  { "team": "Los Angeles Kings", "slug": "los-angeles-kings", "abbr": "L.A", "location": "Los Angeles", "mascot": "Kings", "conference": "Western", "division": "Pacific" },
  { "team": "Phoenix Coyotes", "slug": "phoenix-coyotes", "abbr": "PHX", "location": "Phoenix", "mascot": "Coyotes", "conference": "Western", "division": "Pacific" },
  { "team": "San Jose Sharks", "slug": "san-jose-sharks", "abbr": "S.J", "location": "San Jose", "mascot": "Sharks", "conference": "Western", "division": "Pacific" },
  { "team": "Vancouver Canucks", "slug": "vancouver-canucks", "abbr": "VAN", "location": "Vancouver", "mascot": "Canucks", "conference": "Western", "division": "Pacific" }
]


for team in teams:
  teams_table.insert(team)