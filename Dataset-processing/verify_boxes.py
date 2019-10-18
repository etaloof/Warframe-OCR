import os
import PySimpleGUI as sg
from PIL import Image
import itertools as it
from sys import exit

def launch_ui(img, result):

    layout = [
                  [sg.Text('Entrez le texte'), ],
                  [sg.InputText(focus=True, default_text=result)],
                  [sg.Image(img)],
                  [sg.Submit()],
                  [sg.Quit()]
                 ]

    window = sg.Window('Botty', layout, keep_on_top=True, use_default_focus=False)
    while True:
        event, values = window.Read() # Run the window until an "event" is triggered
        if event == "Submit":
            return values[0]
        elif event == "Quit":
            exit(0)
        elif event is None or event == "Cancel":
            exit(0)

def parse_data_boxes(input_box, img):
    bx = open(input_box,'r', encoding="utf-8")
    result = ''
    for line in bx:
        result += line[0]
    val = launch_ui(img, result)
    bx.close()
    return(val)
    
    
def correct_box_file(input_box, correct_string):
    bxi = open(input_box,'r', encoding="utf-8")
    corrected_string = ''
    box_content = bxi.read()
    iter = list(it.zip_longest(correct_string, box_content.splitlines(), fillvalue='EndLines'))
    for x in iter:
        if x[0][0] == x[1][0]:
            corrected_string = corrected_string + x[1] + '\n'
        elif x[1][0] == '\t':
            corrected_string = corrected_string + x[1] + '\n'
        elif x[0][0] == 'EndLines':
            corrected_string = corrected_string + x[1] + '\n'
        elif x[0][0] != x[1][0]:
            corr_line = x[0][0] + x[1][1:]
            corrected_string = corrected_string + corr_line + '\n'
            
    bxi.close()       
    box_corrected = open(input_box + '.boxy', 'w', encoding="utf-8")
    box_corrected.write(corrected_string)
    box_corrected.close()
    
    
    

dirpath = os.path.join(os.getcwd(), "source")

for node_l1 in os.listdir(dirpath):
    if os.path.isdir(os.path.join(dirpath, node_l1)):
        for node_l2 in os.listdir(os.path.join(dirpath, node_l1)):
            if node_l2.endswith('.box'):
                file_path = os.path.join(dirpath, node_l1, node_l2)
                img = os.path.join(dirpath, node_l1, node_l2).split('.')[0] + ".png"
                user_str = parse_data_boxes(file_path, img)
                correct_box_file(file_path, user_str)
            