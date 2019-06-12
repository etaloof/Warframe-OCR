from bs4 import BeautifulSoup
import requests
import re

page_link = 'https://warframe.fandom.com/wiki/Void_Relic'
page_response = requests.get(page_link, timeout=5)
soup = BeautifulSoup(page_response.content, "html.parser")

r_relic_list = []

parsed = soup.find_all(id="mw-customcollapsible-VaultedRelicList")
parsed_str = str(parsed)
test_str = '<span style="border-bottom: 1px dotted;" class="relic-tooltip tooltips-init-complete" data-param="Lith A1"><a href="/wiki/Lith_A1">Lith A1</a></span>'
x = re.findall("^data-param", test_str)
print(x)
