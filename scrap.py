from bs4 import BeautifulSoup
import requests
import re

page_link = 'https://n8k6e2y6.ssl.hwcdn.net/repos/hnfvc0o3jnfvc873njb03enrf56.html'
page_response = requests.get(page_link, timeout=5)
page_content = BeautifulSoup(page_response.content, "html.parser")


resultt = page_content.find_all(string=re.compile("Relic"))
print(resultt)
