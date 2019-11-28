import pytesseract
import cv2
import numpy as np
from spellcheck import SpellCheck
import uuid
from PIL import Image
import requests

url = 'https://cdn.discordapp.com/attachments/589088834550235158/592486056125792307/relic8.png'


def image_from_url(urls):
    url_response = requests.get(urls, stream=True)
    nparr = np.frombuffer(url_response.content, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image


def get_theme(t):
    if t.load()[115, 86] == (102, 169, 190):
        return 'Brown'
    if t.load()[115, 86] == (35, 31, 153):
        return 'Red'
    if t.load()[115, 86] == (255, 255, 255):
        return 'Blue'
    else:
        return t.load()[115, 86]


s = image_from_url(url)
d = Image.fromarray(s)
print(type(d))
print(get_theme(d))


