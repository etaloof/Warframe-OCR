import cv2
import numpy as np
import colorsys
from colour import Color
import sys
import matplotlib

np.set_printoptions(threshold=sys.maxsize)

input_file = r"ressources\1.png"
image = cv2.imread(input_file) # BGR

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
    (158, 159, 167, 'Equinox'),     # Equinox
    (140, 119, 147, 'Dark lotus')   # Dark lotus
]

ui_color_list_2 = [
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
    for e in ui_color_list:
        if abs(input_clr[2] - e[0]) < color_treshold and abs(input_clr[1] - e[1]) < color_treshold and abs(input_clr[0] - e[2]) < color_treshold:
            return e[3]
        else:
            pass
    
##############################################################################################################


def tresh(image, theme):
    treshold = 55
    e = [item for item in ui_color_list if item[3] == theme][0] 
    upscaled = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC) # Upscaling x2
    lowerBound = np.array([(e[2] - treshold), (e[1] - treshold), (e[0] - treshold)]) # BGR
    upperBound = np.array([(e[2] + treshold), (e[1] + treshold), (e[0] + treshold)]) # BGR
    filter = cv2.inRange(upscaled, lowerBound, upperBound)
    tresh = cv2.bitwise_not(filter)
    kernel = np.ones((3, 3), np.uint8)
    tresh = cv2.erode(tresh, kernel, iterations=1)
    return tresh


def tresh2(image, theme):

    e_primary = [item for item in ui_color_list if item[3] == theme][0]
    e_secondary = [item for item in ui_color_list_2 if item[3] == theme][0]

    c_primary = Color(rgb=(e_primary[0]/255, e_primary[1]/255, e_primary[2]/255))
    c_secondary = Color(rgb=(e_secondary[0]/255, e_secondary[1]/255, e_secondary[2]/255))

    a = image
        
    b = a < 1
    
    np.savetxt("array.txt", a)

    if theme == 'Virtuvian':
        # return abs(test.GetHue() - c_primary.hue) < 2 # && test.GetSaturation() >= 0.25 && test.GetBrightness() >= 0.42;
        pass
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
    
    
def print_array(data):
    with open('test.txt', 'w') as outfile:
        outfile.write('# Array shape: {0}\n'.format(data.shape))
        for data_slice in data:
            np.savetxt(outfile, data_slice, fmt='%-7.2f')
            outfile.write('# New slice\n')


def test_things(image, theme):
    # Warframe-Info values are in HSL format, need to convert everything.
    ori_array = image
    hsl_arr = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
    # Declare colors from RBG lists 1 & 2
    e_primary = [item for item in ui_color_list if item[3] == theme][0]
    e_secondary = [item for item in ui_color_list_2 if item[3] == theme][0]
    c_primary = Color(rgb=(e_primary[0]/255, e_primary[1]/255, e_primary[2]/255))
    c_secondary = Color(rgb=(e_secondary[0]/255, e_secondary[1]/255, e_secondary[2]/255))
    # Get HLS values from item
    h = c_primary.hue * 360
    s = c_primary.saturation 
    l = c_primary.luminance


    #color_p = colorsys.rgb_to_hls(e_p[0]/255., e_p[1]/255., e_p[2]/255.)
    #color_s = colorsys.rgb_to_hls(e_s[0]/255., e_s[1]/255., e_s[2]/255.)
    
    #print(color_p[0])
    #print(color_p[0] * 360)
    
    HueOK = np.logical_and(hsl_arr[..., 0] > 44, hsl_arr[..., 0] < 48)
    SaturationOK = hsl_arr[..., 1] >= (0.25 * 255)
    LightnessOK = hsl_arr[..., 2] >= (0.42 * 255)
    
    combinedMask = HueOK & SaturationOK & LightnessOK
    final_arr = np.where(combinedMask, 0, 255)

    tmp = (HueOK * 255).astype(np.uint8)
    print(tmp.shape)
    print(ori_array[3, 3])
    print(hsl_arr[3, 3])


    cv2.imwrite('test.png', final_arr)
    
    # print_array(final_arr)
    
    # final_img = cv2.cvtColor(final_arr, cv2.COLOR_HLS2BGR)
    
    # cv2.imshow('test', final_img)
            
theme = get_theme(image, 30)
print(theme)
#X, X, nth rgb value
test_things(image, theme)
#cv2.imwrite('tresh.png', tresh)