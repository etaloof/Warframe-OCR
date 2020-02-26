import cv2
import numpy as np
import colorsys
from colour import Color
import sys
import matplotlib

np.set_printoptions(threshold=sys.maxsize)

input_file = "50.jpg"
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
    (200, 169, 237, 'Dark Lotus')
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

# Treshold Function
def get_treshold_2(image, theme):

    e_primary = [item for item in ui_color_list_primary if item[3] == theme][0]
    e_secondary = [item for item in ui_color_list_secondary if item[3] == theme][0]

    c_primary = Color(rgb=(e_primary[0] / 256, e_primary[1] / 256, e_primary[2] / 256))
    c_secondary = Color(rgb=(e_secondary[0] / 256, e_secondary[1] / 256, e_secondary[2] / 256))

    upscaled = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)  # Upscaling x2
    
    rgb_arr = image
    hsl_arr = cv2.cvtColor(upscaled, cv2.COLOR_BGR2HLS)  # Hue, Lighness, Saturation
    
    p_hue = round(c_primary.hue * 360) / 2
    p_hue_sec = round(c_secondary.hue * 360) / 2
    
    kernel = np.ones((3, 3), np.uint8)

    if theme == 'Virtuvian':  # WORKING
        method = 'HSL'
        HueOK = np.logical_and(hsl_arr[..., 0] > p_hue - 4 / 2, hsl_arr[..., 0] < p_hue + 4 / 2)
        SaturationOK = hsl_arr[..., 2] >= (0.25 * 256)
        LightnessOK = hsl_arr[..., 1] >= (0.42 * 256)
        combinedMask = HueOK & SaturationOK & LightnessOK
        
    elif theme == 'Stalker':  # WORKING
        method = 'HSL'
        HueOK = np.logical_and(hsl_arr[..., 0] > p_hue - 4 / 2, hsl_arr[..., 0] < p_hue + 4 / 2)
        SaturationOK = hsl_arr[..., 2] >= (0.5 * 256)
        LightnessOK = hsl_arr[..., 1] >= (0.20 * 256)
        combinedMask = HueOK & SaturationOK & LightnessOK
        
    elif theme == 'Baruk':
        pass
        
    elif theme == 'Corpus':
        pass
        
    elif theme == 'Fortuna':  # WORKING
        method = 'HSL'
        HueOK = np.logical_and(hsl_arr[..., 0] > p_hue - 4 / 2, hsl_arr[..., 0] < p_hue + 4 / 2)
        SaturationOK = hsl_arr[..., 2] >= (0.20 * 256)
        LightnessOK = hsl_arr[..., 1] >= (0.25 * 256)
        combinedMask = HueOK & SaturationOK & LightnessOK
        
    elif theme == 'Grineer':
        pass
        
    elif theme == 'Lotus':  # A TESTER
        method = 'HSL'
        HueOK = np.logical_and(hsl_arr[..., 0] > p_hue - 5 / 2, hsl_arr[..., 0] < p_hue + 5 / 2)
        SaturationOK = hsl_arr[..., 2] >= (0.65 * 256)
        LightnessOK = np.logical_and(hsl_arr[..., 1] >= p_lumi - 0.1, hsl_arr[..., 0] <= p_lumi + 0.1)
        # return Math.Abs(test.GetHue() - primary.GetHue()) < 5 & test.GetSaturation() >= 0.65 & & Math.Abs(
        #    test.GetBrightness() - primary.GetBrightness()) <= 0.1
        # | | (Math.Abs(test.GetHue() - secondary.GetHue()) < 4 & & test.GetBrightness() >= 0.65);
        combinedMask = HueOK & SaturationOK & LightnessOK
        
    elif theme == 'Nidus':
        method = 'BGR'
        lowerBound = np.array([(e_primary[2] - 40), (e_primary[1] - 40), (e_primary[0] - 40)])  # BGR
        upperBound = np.array([(e_primary[2] + 40), (e_primary[1] + 40), (e_primary[0] + 40)])  # BGR

    elif theme == 'Orokin':
        pass
        
    elif theme == 'Tenno':
        pass
        
    elif theme == 'High contrast':
        pass
        
    elif theme == 'Legacy':  # WORKS but NEED TESTING
        method = 'HSL'
        SaturationOK = hsl_arr[..., 2] <= (0.2 * 256)
        LightnessOK = hsl_arr[..., 1] >= (0.75 * 256)
        combinedMask = SaturationOK & LightnessOK
        pass
        
    elif theme == 'Equinox':  # WORKING
        method = 'HSL'
        HueOK = np.logical_and(hsl_arr[..., 0] > 110, hsl_arr[..., 0] < 135)
        SaturationOK = hsl_arr[..., 2] <= (0.1 * 255)
        LightnessOK = np.logical_and(hsl_arr[..., 1] >= (0.35 * 256), hsl_arr[..., 1] <= (0.74 * 256))
        combinedMask = HueOK & SaturationOK & LightnessOK

    elif theme == 'Dark Lotus':  # WORKING
        method = 'HSL'
        HueOK = np.logical_and(hsl_arr[..., 0] > 134, hsl_arr[..., 0] < 143)
        SaturationOK = np.logical_and(hsl_arr[..., 2] >= (0.11 * 256), hsl_arr[..., 2] <= (0.22 * 256))
        LightnessOK = np.logical_and(hsl_arr[..., 1] >= (0.43 * 256), hsl_arr[..., 2] <= (0.53 * 256))
        combinedMask = HueOK & SaturationOK & LightnessOK
    
    if method == 'BGR':
        filter = cv2.inRange(upscaled, lowerBound, upperBound)
        filered = cv2.bitwise_not(filter)
        tresh = cv2.erode(filered, kernel, iterations=1)
        
    elif method == 'HSL':
        hsl_arr[combinedMask] = 0
        hsl_arr[~combinedMask] = 255
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
treshold_1 = get_treshold(image, theme)
treshold_2 = get_treshold_2(image, theme)
cv2.imwrite('tresh_1.png', treshold_1)
cv2.imwrite('tresh_2.png', treshold_2)
