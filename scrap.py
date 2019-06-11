from bs4 import BeautifulSoup
import requests
import re

page_link = 'https://n8k6e2y6.ssl.hwcdn.net/repos/hnfvc0o3jnfvc873njb03enrf56.html'
page_response = requests.get(page_link, timeout=5)
page_content = BeautifulSoup(page_response.content, "html.parser")

r_relic_list = []
for text in page_content.findAll('td', string=re.compile("Relic$")):
    b = text.get_text()
    r_relic_list.append(b)
d_relic_list = list(dict.fromkeys(r_relic_list))
n_relic_list = sorted(d_relic_list)
print(n_relic_list)
