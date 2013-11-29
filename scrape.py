from BeautifulSoup import BeautifulSoup
import re
import requests

def scrape_game_page(url):
  r  = requests.get(url)
  if r.status_code==200:
    soup = BeautifulSoup(r.content)
    tables = soup.findAll('table')
    datas = {}
    for i, t in enumerate(tables):
      headers = []

      for el in t.find('thead').findAll('th'):

        if el.text != "":
          headers.append(el.text)

        else:
          headers.append('null')

      rows = [el for el in t.find('tbody').findAll('tr') if el.text!='']

      data = []
      for r in rows:
        cells = [el.text for el in r.findAll('td')]
        row_dict = {}

        for i, c in enumerate(cells):
          row_dict[headers[i]] = c

        row_dict.pop('null', None)
        data.append(row_dict)

      datas['table' + str(i)] = data

    return datas


