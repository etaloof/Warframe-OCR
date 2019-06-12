from bs4 import BeautifulSoup
import requests
import re

page_link = 'https://warframe.fandom.com/wiki/Void_Relic'
page_response = requests.get(page_link, timeout=5)
soup = BeautifulSoup(page_response.content, "html.parser")

r_relic_list = []

table = soup.find('div', id='mw-customcollapsible-VaultedRelicList')
relics = table.find_all('span', class_='relic-tooltip')
for relic in relics:
    r_relic_list.append(relic.get('data-param'))
print(r_relic_list)

