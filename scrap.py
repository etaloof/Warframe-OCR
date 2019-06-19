from bs4 import BeautifulSoup
import requests

f = open('relics.html', 'r', encoding="UTF-8")
s = f.read()
soup = BeautifulSoup(s, "html.parser")

# page_link = 'https://warframe.fandom.com/wiki/Void_Relic'
# page_response = requests.get(page_link, timeout=5)
# soup = BeautifulSoup(page_response.content, "html.parser")


def update_vault_list():
    v_relic_list = []
    table = soup.find('div', id='mw-customcollapsible-VaultedRelicList')
    relics = table.findAll('span', class_='relic-tooltip')
    for relic in relics:
        v_relic_list.append(relic.get('data-param'))
    print('[Init] Mise a jour des vaulted réussie !')
    return v_relic_list


