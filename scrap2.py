from bs4 import BeautifulSoup
import requests
import re

page_link = 'https://warframe.fandom.com/wiki/Void_Relic'
page_response = requests.get(page_link, timeout=5)
page_content = BeautifulSoup(page_response.content, "html.parser")

r_relic_list = []
for text in page_content.findAll("span", class_="relic-tooltip"):
    b = text.get_text()
    r_relic_list.append(b)
#d_relic_list = list(dict.fromkeys(r_relic_list))
#n_relic_list = sorted(d_relic_list)
print(r_relic_list)
