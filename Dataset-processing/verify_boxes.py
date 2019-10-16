import os
import PySimpleGUI as sg
from PIL import Image

def launch_ui(img, result):

    layout = [
                  [sg.Text('Entrez le texte'), ],
                  [sg.InputText(focus=True, default_text=result)],
                  [sg.Image(img)],
                  [sg.Submit()]
                 ]

    window = sg.Window('Botty', layout, keep_on_top=True, use_default_focus=False)
    event, values = window.Read()
    window.Close()
    return values[0]

def parse_data_boxes(input_box, img):
    result = ''
    for line in input_box:
        result += line[0]
    val = launch_ui(img, result)
    print(val)

dirpath = os.path.join(os.getcwd(), "source")

for node_l1 in os.listdir(dirpath):
    if os.path.isdir(os.path.join(dirpath, node_l1)):
        for node_l2 in os.listdir(os.path.join(dirpath, node_l1)):
            if node_l2.endswith('.box'):
                file = open(os.path.join(dirpath, node_l1, node_l2),'r')
                img = os.path.join(dirpath, node_l1, node_l2).split('.')[0] + ".png"
                # parse_data_boxes(file, img)
                print(file.read())
            