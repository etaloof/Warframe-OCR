import os
import PySimpleGUI as sg
from PIL import Image

# Chemin d'accés du dossier avec les petites images
mypath = "C:\\Users\\PRAN152\\Pictures\\organized-data\\"

# Chemin d'accés du dossier (vide) avec le texte généré
mypath2 = "C:\\Users\\PRAN152\\Pictures\\transloc\\"

i = 1


def launch_ui(img):

    layout = [
                  [sg.Text('Entrez le texte'), ],
                  [sg.InputText(focus=True)],
                  [sg.Image(img)],
                  [sg.Submit()]
                 ]

    window = sg.Window('Botty', layout, keep_on_top=True, use_default_focus=False)
    event, values = window.Read()
    window.Close()
    return values[0]


for filename in os.listdir(mypath):
    src = mypath + filename
    dst = mypath + str(i)
    im = Image.open(src)
    rgb_im = im.convert('RGB')
    rgb_im.save(dst + '.png')
    img_view = dst + '.png'
    val = launch_ui(img_view)
    outF = open(mypath2 + str(i) + '.gt.txt', "w")
    outF.write(val)
    outF.close()
    im2 = Image.open(img_view)
    rgb_im2 = im2.convert('RGB')
    rgb_im2.save(dst + '.tif')
    os.remove(dst + '.png')
    i += 1
