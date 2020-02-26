import PySimpleGUI as sg
from sys import exit
from PIL import Image
import base64
import cv2
from io import BytesIO
import numpy as np

# Load image as numpy format
image_source = cv2.imread("50.jpg")
rgb_source = cv2.cvtColor(image_source, cv2.COLOR_BGR2RGB)
# Downscale image for interface
downscale = cv2.resize(rgb_source, (1024, 576), interpolation=cv2.INTER_CUBIC)
# kernel = np.ones((1, 1), np.uint8)
# kernelled = cv2.erode(downscale, kernel, iterations=1)
# Convert it to PIL format
pil_img = Image.fromarray(downscale)


def encode_to_64(img):
    # Convert image to Base64 string
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue())
    return img_str


def apply_filter(img, slider_dict):
    # hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    lower_virtu = np.array([slider_dict['slider1-down'], slider_dict['slider2-down'], slider_dict['slider3-down']])
    upper_virtu = np.array([slider_dict['slider1-up'], slider_dict['slider2-up'], slider_dict['slider3-up']])
    mask = cv2.inRange(img, lower_virtu, upper_virtu)
    imgtresh = cv2.bitwise_not(mask)
    filter_pil_img = Image.fromarray(imgtresh)
    filter_new_img = encode_to_64(filter_pil_img)
    return filter_new_img


layout = [[sg.Text('B '), sg.Slider(range=(0, 255), default_value=0, orientation='h', size=(30, 20), key='slider1-down', enable_events=True), sg.Text(' TO '), sg.Slider(range=(0, 255), default_value=0, orientation='h', size=(30, 20), key='slider1-up', enable_events=True)],
          [sg.Text('G '), sg.Slider(range=(0, 255), default_value=80, orientation='h', size=(30, 20), key='slider2-down', enable_events=True), sg.Text(' TO '), sg.Slider(range=(0, 255), default_value=255, orientation='h', size=(30, 20), key='slider2-up', enable_events=True)],
          [sg.Text('R '), sg.Slider(range=(0, 255), default_value=80, orientation='h', size=(30, 20), key='slider3-down', enable_events=True), sg.Text(' TO '), sg.Slider(range=(0, 255), default_value=255, orientation='h', size=(30, 20), key='slider3-up', enable_events=True)],
          [sg.Image(data=encode_to_64(pil_img), key='image')],
          [sg.Quit()]
          ]

# Display the window and get values
window = sg.Window('Filter-Creator', layout)

while True:
    event, values = window.Read()
    new_img = apply_filter(downscale, values)
    window.FindElement('image').Update(data=new_img)
    if event is 'slider1-up' or 'slider1-down' or 'slider2-up' or 'slider2-down' or 'slider3-up' or 'slider3-down':
        window.FindElement('image').Update(data=new_img)
    if event is None:
        break
    if event == 'Quit':
            exit(0)
