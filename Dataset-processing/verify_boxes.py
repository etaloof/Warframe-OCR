import os
import PySimpleGUI as sg
import itertools as it
from sys import exit


# Create a list of the img files available to works on
def create_work_list(dirpath):
    list_img = []
    for node_l1 in os.listdir(dirpath):
        if os.path.isdir(os.path.join(dirpath, node_l1)):
            list_img.append(node_l1)
    return list_img


# Launch an UI to choose wich img file number to works on
def launch_menu(choice_list):
    
    layout = [
                  [sg.Text('Choisissez une image a traiter !'), ],
                  [sg.InputCombo(choice_list, size=(20, 1)), ],     
                  [sg.Submit()],
                  [sg.Quit()]
                 ]
    window = sg.Window('Choix du fichier', layout, use_default_focus=False)
    while True:
        event, values = window.Read()
        if event == 'Submit':
            window.Close()
            return values[0]
        if event == 'Quit':
            exit(0)


# Launch an UI to let the user correct the box string
def launch_ui(img, box_text):

    layout = [
                  [sg.Text('Entrer la bonne valeur !'), ],
                  [sg.InputText(focus=True, default_text=box_text)],
                  [sg.Image(img)],
                  [sg.Submit()],
                  [sg.Quit()]
                 ]
    window = sg.Window('Verificateur', layout, use_default_focus=False)
    while True:
        event, values = window.Read()
        if event == 'Submit':
            window.Close()
            return values[0]
        if event == 'Quit':
            exit(0)


# Parse a wrong box file string and launch the ui to correct   
def parse_data_boxes(input_box, img):
    bx = open(input_box, 'r', encoding="utf-8")
    result = ''
    for line in bx:
        result += line[0]
    val = launch_ui(img, result)
    bx.close()
    return val
    
    
# Create a new file ".boxy" with a corrected box string inside   
def correct_box_file(input_box, correct_string):
    bxi = open(input_box, 'r', encoding="utf-8")
    corrected_string = ''
    box_content = bxi.read()
    iter_boxes = list(it.zip_longest(correct_string, box_content.splitlines(), fillvalue='EndLines'))
    for x in iter_boxes:
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


def main():

    # Generate dirpath to the source img files
    dirpath = os.path.join(os.getcwd(), "source")
    
    # Store the list of imgs files to works in var
    img_list = create_work_list(dirpath)

    # Store the img to works on next in var
    img_choice = launch_menu(img_list)
                            
    if os.path.isdir(os.path.join(dirpath, img_choice)):  # --> Check if choosen img dir is a dir
        for node_l2 in os.listdir(os.path.join(dirpath, img_choice)):  # --> Loop on the files inside the dir detected
            if node_l2.endswith('.box'):
                file_path = os.path.join(dirpath, img_choice, node_l2)
                img = os.path.join(dirpath, img_choice, node_l2).split('.')[0] + ".png"
                user_str = parse_data_boxes(file_path, img)
                correct_box_file(file_path, user_str)
      
            
if __name__ == "__main__":
    main()
