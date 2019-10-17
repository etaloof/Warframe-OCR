import os
import PySimpleGUI as sg
from PIL import Image
import re
import itertools as it


user_input = 'Relique Meso N1 [Eclatante]'
user_input_list = user_input.split()

corrected_string = ''

file = open(r'C:\Users\aprieto\Documents\GitHub\Warframe-OCR\Dataset-processing\test2.box', 'r', encoding="utf-8")
file_content = file.read()

test = list(it.zip_longest(user_input, file_content.splitlines(), fillvalue='EndLines'))
print(test)

for x in test:
    if x[0][0] == x[1][0]:
        corrected_string = corrected_string + x[1] + '\n'
    elif x[1][0] == '\t':
        corrected_string = corrected_string + x[1] + '\n'
    elif x[0][0] == 'EndLines':
        corrected_string = corrected_string + x[1] + '\n'
    elif x[0][0] != x[1][0]:
        corr_line = x[0][0] + x[1][1:]
        corrected_string = corrected_string + corr_line + '\n'

print(corrected_string)

file2 = open(r'C:\Users\aprieto\Documents\GitHub\Warframe-OCR\Dataset-processing\test2.box', 'w', encoding="utf-8")
file2.write(corrected_string)
file.close()
file2.close()

