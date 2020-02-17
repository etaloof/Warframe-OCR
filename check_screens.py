import cv2
import numpy as np

input_file = r"ressources\4.png"
image = cv2.imread(input_file)

#UI-COLORS####################################################################################################

# RGB Format
ui_color_list = [
    (189, 168, 101, 'Virtuvian'),   # Vitruvian
    (150, 31, 35, 'Stalker'),       # Stalker 
    (238, 193, 105, 'Baruk'),       # Baruk
    (35, 200, 245, 'Corpus'),       # Corpus
    (57, 105, 192, 'Fortuna'),      # Fortuna
    (255, 189, 102, 'Grineer'),     # Grineer
    (36, 184, 242, 'Lotus'),        # Lotus
    (140, 38, 92, 'Nidus'),         # Nidus
    (20, 41, 29, 'Orokin'),         # Orokin
    (9, 78, 106, 'Tenno'),          # Tenno
    (2, 127, 217, 'High contrast'), # High contrast
    (255, 255, 255, 'Legacy'),      # Legacy
    (158, 159, 167, 'Equinox')      # Equinox
]


# Check ui theme from screenshot (Image Format : OPENCV)
def get_theme(image, color_treshold):
    input_clr = image[86, 115] # Y,X  RES-DEPENDANT
    for e in ui_color_list:
        if abs(input_clr[2] - e[0]) < color_treshold and abs(input_clr[1] - e[1]) < color_treshold and abs(input_clr[0] - e[2]) < color_treshold:
            return e[3]
        else:
            pass
    
##############################################################################################################
def tresh(image, theme):
    e = [item for item in ui_color_list if item[3] == theme][0] 
    upscaled = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC) # Upscaling x2
    lowerBound = np.array([(e[2] - 30), (e[1] - 30), (e[0] - 30)]) # BGR
    upperBound = np.array([(e[2] + 30), (e[1] + 30), (e[0] + 30)]) # BGR
    filter = cv2.inRange(upscaled, lowerBound, upperBound)
    tresh = cv2.bitwise_not(filter)
    kernel = np.ones((3, 3), np.uint8)
    tresh = cv2.erode(tresh, kernel, iterations=1)
    return tresh
 
theme = get_theme(image, 30)
print(theme)
tresh = tresh(image, theme)
cv2.imwrite('tresh.png', tresh)