from bs4 import BeautifulSoup, Tag
import re
import requests
import itertools
import inspect
import dataset


db = dataset.connect('postgresql://shortsof_admin:Ny24CnE86a8He@50.87.139.53/shortsof_khokkey')

# db.query('update games set events = null')
#db.query('alter table games add column events text[]')
db.query('alter table games alter column events type regdictionary[][]')

#statement = db.query('select column_name, data_type from information_schema.columns')

for g in db["games"]:
  print g

#print db["games"].information_schema
# for game in db["games"]:
#   print game.information_schema

# for result in results:
#   print result
# for team in db['teams']:
#   print team['abbr']

#alter table db["games"] modify column events text[][]

# print db["games"].columns