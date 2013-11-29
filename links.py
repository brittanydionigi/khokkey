from BeautifulSoup import BeautifulSoup
import re
import requests
from scrape import scrape_game_page

base_url = "http://www.extraskater.com"
urls = [base_url + "/games/all?page=" + str(i) for i in [1,2]]

def get_game_links(url):
  r = requests.get(url)
  if r.status_code==200:
    soup = BeautifulSoup(r.content)

    game_links = soup.find('ul', { 'id': 'games-list'}).findAll('a')

    return [base_url + g['href'] for g in game_links]

if __name__ == '__main__':
  for u in urls:
    links = get_game_links(u)
    for l in links:
      print l
      game_stats = scrape_game_page(l)
      print game_stats



