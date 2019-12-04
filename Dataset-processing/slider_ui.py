import PySimpleGUI as sg
from sys import exit
from PIL import Image
import base64
from io import BytesIO

# Load IMG as PIL
image = Image.open("theme_source.png")

# Resize it
image = image.resize((1024, 576))

# Convert it to Base64 string
buffered = BytesIO()!
image.save(buffered, format="PNG")
img_str = base64.b64encode(buffered.getvalue())


layout = [[sg.Text('TEINTE     '), sg.Slider(range=(0,255), default_value=0, orientation='h', size=(30,20), key='slider1-down', enable_events=True), sg.Text(' TO '), sg.Slider(range=(0,255), default_value=0, orientation='h', size=(30,20), key='slider1-up', enable_events=True)],
          [sg.Text('SATURATION '), sg.Slider(range=(0,255), default_value=0, orientation='h', size=(30,20), key='slider2-down', enable_events=True), sg.Text(' TO '), sg.Slider(range=(0,255), default_value=0, orientation='h', size=(30,20), key='slider2-up', enable_events=True)], 
          [sg.Text('VALEUR     '), sg.Slider(range=(0,255), default_value=0, orientation='h', size=(30,20), key='slider3-down', enable_events=True), sg.Text(' TO '), sg.Slider(range=(0,255), default_value=0, orientation='h', size=(30,20), key='slider3-up', enable_events=True)], 
          [sg.Image(data = img_str)],
          [sg.Quit()]
          ]

# Display the window and get values
window = sg.Window('Test-app', layout)

while True:
    event, values= window.Read()
    window.FindElement('slider1-down').Update(sz)
    window.FindElement('slider1-up').Update(sz)
    window.FindElement('slider2-down').Update(sz)
    window.FindElement('slider2-up').Update(sz)
    window.FindElement('slider3-down').Update(sz)
    window.FindElement('slider3-up').Update(sz)
    if event is None:
        break
    if event == 'Quit':
            exit(0)