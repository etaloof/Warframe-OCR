import cv2
import numpy as np
import colorsys
from colour import Color
import sys
import matplotlib

np.set_printoptions(threshold=sys.maxsize)

input_file = "1.png"
image = cv2.imread(input_file)  # BGR

#UI-COLORS####################################################################################################

# RGB Format
ui_color_list_primary = [
    (190, 169, 102, 'Virtuvian'),             # Vitruvian
    (153,  31,  35, 'Stalker'),               # Stalker 
    (238, 193, 105, 'Baruk'),                 # Baruk
    ( 35, 201, 245, 'Corpus'),                # Corpus
    ( 57, 105, 192, 'Fortuna'),               # Fortuna
    (255, 189, 102, 'Grineer'),               # Grineer
    ( 36, 184, 242, 'Lotus'),                 # Lotus
    (140,  38,  92, 'Nidus'),                 # Nidus
    ( 20,  41,  29, 'Orokin'),                # Orokin
    (  9,  78, 106, 'Tenno'),                 # Tenno
    (  2, 127, 217, 'High contrast'),         # High contrast
    (255, 255, 255, 'Legacy'),                # Legacy
    (158, 159, 167, 'Equinox'),               # Equinox
    (140, 119, 147, 'Dark Lotus')             # Dark Lotus
]

ui_color_list_secondary = [
    (245, 227, 173, 'Virtuvian'),   
    (255,  61,  51, 'Stalker'),     
    (236, 211, 162, 'Baruk'),       
    (111, 229, 253, 'Corpus'),      
    (255, 115, 230, 'Fortuna'),     
    (255, 224, 153, 'Grineer'),     
    (255, 241, 191, 'Lotus'),           
    (245,  73,  93, 'Nidus'),           
    (178, 125,   5, 'Orokin'),  
    (  6, 106,  74, 'Tenno'),           
    (255, 255,   0, 'High contrast'),   
    (232, 213,  93, 'Legacy'),      
    (232, 227, 227, 'Equinox'), 
    (200, 169, 237, 'Dark lotus')
]


# Check ui theme from screenshot (Image Format : OPENCV)
def get_theme(image, color_treshold):
    input_clr = image[86, 115] # Y,X  RES-DEPENDANT
    for e in ui_color_list_primary:
        if abs(input_clr[2] - e[0]) < color_treshold and abs(input_clr[1] - e[1]) < color_treshold and abs(input_clr[0] - e[2]) < color_treshold:
            return e[3]
        else:
            pass
    
##############################################################################################################


# Treshold function
def get_treshold(image, theme):
    e = [item for item in ui_color_list_primary if item[3] == theme][0]
    upscaled = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)  # Upscaling x2
    lowerBound = np.array([(e[2] - 30), (e[1] - 30), (e[0] - 30)])  # BGR
    upperBound = np.array([(e[2] + 30), (e[1] + 30), (e[0] + 30)])  # BGR
    filter = cv2.inRange(upscaled, lowerBound, upperBound)
    tresh = cv2.bitwise_not(filter)
    print(tresh)
    kernel = np.ones((3, 3), np.uint8)
    tresh = cv2.erode(tresh, kernel, iterations=1)
    return tresh


def get_treshold_2(image, theme):

    e_primary = [item for item in ui_color_list_primary if item[3] == theme][0]
    e_secondary = [item for item in ui_color_list_secondary if item[3] == theme][0]
    
    c_primary = Color(rgb=(e_primary[0]/256, e_primary[1]/256, e_primary[2]/256))
    c_secondary = Color(rgb=(e_secondary[0]/256, e_secondary[1]/256, e_secondary[2]/256))
    
    upscaled = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)  # Upscaling x2
    hsl_arr = cv2.cvtColor(upscaled, cv2.COLOR_BGR2HLS)  # Hue, Lighness, Saturation

    print(hsl_arr.dtype, hsl_arr.shape)

    if theme == 'Virtuvian':
        p_hue = round(c_primary.hue * 360)/2
        HueOK = np.logical_and(hsl_arr[..., 0] > p_hue - 4/2, hsl_arr[..., 0] < p_hue + 4/2)
        SaturationOK = hsl_arr[..., 2] >= (0.25 * 256)
        LightnessOK = hsl_arr[..., 1] >= (0.42 * 256)

    if theme == 'Stalker':
        pass
    if theme == 'Baruk':
        pass
    if theme == 'Corpus':
        pass
    if theme == 'Fortuna':
        pass
    if theme == 'Grineer':
        pass
    if theme == 'Lotus':
        pass
    if theme == 'Nidus':
        pass
    if theme == 'Orokin':
        pass
    if theme == 'Tenno':
        pass
    if theme == 'High contrast':
        pass
    if theme == 'Legacy':
        pass
    if theme == 'Equinox':
        pass
    if theme == 'Dark lotus':
        pass


    combinedMask = HueOK & SaturationOK & LightnessOK

    hsl_arr[combinedMask] = 0
    hsl_arr[~combinedMask] = 255

    print(hsl_arr[0][0])

    kernel = np.ones((3, 3), np.uint8)
    tresh = cv2.erode(hsl_arr, kernel, iterations=1)
    
    return tresh
    
    
def print_array(data):
    with open('test.txt', 'w') as outfile:
        outfile.write('# Array shape: {0}\n'.format(data.shape))
        for data_slice in data:
            np.savetxt(outfile, data_slice, fmt='%-7.2f')
            outfile.write('# New slice\n')


theme = get_theme(image, 30)
print(theme)
treshold = get_treshold_2(image, theme)
cv2.imwrite('tresh.png', treshold)
