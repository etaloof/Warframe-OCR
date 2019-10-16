import os
import PySimpleGUI as sg
from PIL import Image
import re

file = open(r'C:\Users\aprieto\Documents\GitHub\Warframe-OCR\Dataset-processing\test.box', 'r')
file_content = file.read()
for line in file_content.splitlines():
    line_content = line
    print(line_content.split())

