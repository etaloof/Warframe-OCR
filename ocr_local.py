import pytesseract
import cv2
import numpy as np
from PIL import Image
from spellchecker import SpellChecker
import logging
import shutil
import names
from random import randint
import re
from colour import Color
from pathlib import Path
import os
from pprint import pprint

# Enable logging
log = logging.getLogger("BlackBot_log")
log.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(message)s", "%Y-%m-%d %H:%M:%S")
console.setFormatter(formatter)
log.addHandler(console)

fh = logging.FileHandler('Warframe-Bot.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s.%(msecs)03d - %(name)s:%(lineno)d - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
fh.setFormatter(formatter)
log.addHandler(fh)

#CORRECTION_LIST##############################################################################################

ref_1_list = ['relique', 'relic']
ref_2_list = ['lith', 'axi', 'neo', 'meso']

#IMAGE########################################################################################################

image_input = cv2.imread('ressources/41.png')
folder = Path(__file__).parent
pytesseract.pytesseract.tesseract_cmd = os.path.join(r'C:\Users\aprieto\Documents\GitHub\WF-RelicData\Tesseract-OCR', 'tesseract.exe')

##############################################################################################################
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
#####TRESHOLD#################################################################################################


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

##############################################################################################################


def findOccurrences(s, ch):
    return [i for i, letter in enumerate(s) if letter == ch]
    

# Hallucination error correction
def sanity_restore(string):
    string = string.upper()
    
    for idx, char in enumerate(string):
        if idx == 0:
            if char == ']':
                string = string[:0] + "1" + string[1:]
            if char == '[':
                string = string[:0] + "I" + string[1:]
            if char == '6':
                string = string[:0] + "G" + string[1:]
            if char == '1':
                string = string[:0] + "T" + string[1:]
        if idx == 1:
            if char == 'G':
                string = string[:1] + "6" + string[2:]
            if char == 'T':
                string = string[:1] + "1" + string[2:]
        if idx == 2:
            if char == 'G':
                string = string[:2] + "6" + string[3:]
            if char == 'T':
                string = string[:2] + "1" + string[3:]
                
    return string
        
        
# Extract values from the ocr result
def extract_vals(text):
    p_string = text.casefold().rstrip()


    if ocr_extract_quality(p_string) is not None:
        quality = ocr_extract_quality(p_string)
    else:
        quality = 'OcrError'

    if ocr_extract_era(p_string) is not None:
        era = ocr_extract_era(p_string)
    else:
        era = 'OcrError'

    if ocr_extract_name(p_string) is not None:
        name = ocr_extract_name(p_string)
    else:
        name = 'OcrError'

    return era, name, quality


# Extract NAME from the ocr result (NO SPELLCHECK)
def ocr_extract_name(string):
    rel_eng = spell_correction_ocr(' '.join(string.split(" ")[2:])[:5].lower(), ref_1_list).lower()
    rel_fr = spell_correction_ocr(string.split(" ")[0].lower(), ref_1_list).lower()
    if 'relique' in rel_fr:
        name_string =  ' '.join(string.split(" ")[2:])[:3].capitalize().rstrip()
        # Check for sanity
        name_string_sanity = sanity_restore(name_string)
        return name_string_sanity
    if 'relic' in rel_eng:
        name_string =  string.split(" ")[1][:3].capitalize().rstrip()
        name_string_sanity = sanity_restore(name_string)
        # Check for sanity
        return name_string_sanity


# Extract ERA from the ocr result (WITH SPELLCHECK)
def ocr_extract_era(string):
    rel_eng = spell_correction_ocr(' '.join(string.split(" ")[2:])[:5].lower(), ref_1_list).lower()
    rel_fr = spell_correction_ocr(string.split(" ")[0].lower(), ref_1_list).lower()
    
    # Handle french
    if 'relique' in rel_fr:
        found_era = spell_correction_ocr(string.split(" ")[1].lower(), ref_2_list)
        return found_era
    
    # Handle english
    if 'relic' in rel_eng:
        found_era = spell_correction_ocr(string.split(" ")[0].lower(), ref_2_list)
        return found_era


# Try to correct mistakes
def spell_correction_ocr(string, corr_list):
    spell_check_ocr = SpellChecker(distance=2, language=None, case_sensitive=False)
    spell_check_ocr.word_frequency.load_words(corr_list)
    spell_check_ocr.correction(string)
    return spell_check_ocr.correction(string).strip().capitalize()


# Check for specific sprite to see if the relic exist
def check_for_sign(img):
    precision = 0.96
    path_to_img = r'./relic_template.png'
    path_to_mask = r'./relic_mask.png'
    template = cv2.imread(path_to_img, 0)
    mask = cv2.imread(path_to_mask, 0)
    w, h = template.shape[::-1]
    res = cv2.matchTemplate(img, template, cv2.TM_CCORR_NORMED, mask=mask)
    loc = np.where(res >= precision)
    count = 0
    for pt in zip(*loc[::-1]):  # Swap columns and rows
        cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
        count = count + 1
    return count


# Extract QUALITY from the ocr result (NO SPELLCHECK FOR NOW)
def ocr_extract_quality(string):
    if any(s in string for s in ['exceptionnelle', 'éxceptionnelle', 'exceptional']):
        return 'Exceptionnelle'
    if any(s in string for s in ['eclatante', 'éclatante', 'radiant']):
        return 'Eclatante'
    if any(s in string for s in ['impeccable', 'flawless']):
        return 'Impeccable'
    else:
        return 'Intacte'


# Crop an area of a relic
def relicarea_crop(upper_y, downer_y, left_x, right_x, img):
    # upperY:downerY, LeftX:RightX
    cropped = img[upper_y:downer_y, left_x:right_x]
    return cropped


def data_pass_nb(pos1, pos2, pos3, pos4, image, theme, id):
    # Generate rID
    rid = str(randint(100, 999))
    # Crop the relic part
    cropped_img = relicarea_crop(pos1, pos2, pos3, pos4, image)
    greyed_image = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
    upscaled = cv2.resize(cropped_img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    if check_for_sign(greyed_image) >= 1:
        return False
    else:
        
        log.debug('[' + id + '] ' + '[ Theme used is : ' + theme + ' ]')  # DEBUG

        tessdata_dir_config = '--tessdata-dir "C:/Users/aprieto/Documents/GitHub/Warframe-OCR/tessdata" -l Roboto --psm 6 --oem 1 get.images'

        text = pytesseract.image_to_string(get_treshold_2(cropped_img, theme), config=tessdata_dir_config)

        log.debug('[' + id + '] ' + '[ Tesseract output for NB is : ' + text + ' ]')
        
        corrected_nbr = re.sub("G", "6", text)  # Replacing letter G by 6
        corrected_nbr = re.sub("[^0-9]", "", corrected_nbr)  # Removing non-numbers characters from the OCR-test

        return corrected_nbr.casefold()


class OcrCheck:
    def __init__(self, image):
        self.image = image
        self.relic_list = []
        self.theme = get_theme(self.image, 30)
        self.imgID = names.get_last_name()
        # Ecart X entre les reliques d'une même ligne : 218, y : 201
        # Block1 = Nombre, Block2 = Nom | LeftX, UpperY, RightX, DownerY
        self.pos_list = [((99, 204, 139, 226), (101, 319, 259, 365)),
                         ((317, 204, 357, 226), (318, 319, 477, 365)),
                         ((534, 204, 574, 226), (536, 319, 695, 365)),
                         ((750, 204, 790, 226), (747, 319, 906, 365)),
                         ((966, 204, 1006, 226), (965, 319, 1124, 365)),

                         ((99, 407, 139, 429), (101, 522, 259, 568)),
                         ((317, 407, 357, 429), (318, 522, 477, 568)),
                         ((534, 407, 574, 429), (536, 522, 695, 568)),
                         ((750, 407, 790, 429), (747, 522, 906, 568)),
                         ((966, 407, 1006, 429), (965, 522, 1124, 568)),

                         ((99, 609, 139, 631), (101, 724, 259, 770)),
                         ((317, 609, 357, 631), (318, 724, 477, 770)),
                         ((534, 609, 574, 631), (536, 724, 695, 770)),
                         ((750, 609, 790, 631), (747, 724, 906, 770)),
                         ((966, 609, 1006, 631), (965, 724, 1124, 770)),

                         ((99, 813, 139, 832), (101, 928, 259, 974)),
                         ((317, 813, 357, 832), (318, 928, 477, 974)),
                         ((534, 813, 574, 832), (536, 928, 695, 974)),
                         ((750, 813, 790, 832), (747, 928, 906, 974)),
                         ((966, 813, 1006, 832), (965, 928, 1124, 974))
                         ]

    def data_pass_name(self, pos1, pos2, pos3, pos4, quantity, image, theme, img_id):
        # Generate rID
        rid = str(randint(100, 999))
        # Crop relic parts
        cropped_img = relicarea_crop(pos1, pos2, pos3, pos4, image)
        # Actual OCR
        tessdata_dir_config = '--tessdata-dir "C:/Users/aprieto/Documents/GitHub/Warframe-OCR/tessdata" -l Roboto --oem 1 --psm 6 -c tessedit_char_blacklist=jJyY'
        textocr = pytesseract.image_to_string(get_treshold_2(cropped_img, theme), config=tessdata_dir_config)
        # Write log for result
        log.debug('[' + img_id + '] ' + '[ Tesseract output for TEXT is : ' + textocr + ' ]')  # DEBUG
        if textocr == '':
            pass
        else:
            corrected_text = re.sub("\n", " ", textocr)
            corrected_text = re.sub("'", " ", corrected_text)
            self.relic_list.append(extract_vals(corrected_text) + (quantity,))

    def ocr_loop(self):
        print(self.theme)
        for i in self.pos_list:
            nb = data_pass_nb(i[0][1], i[0][3], i[0][0], i[0][2], self.image, self.theme, self.imgID)
            if nb is False:
                pass
            elif nb == '':
                quantity = '1'
                self.data_pass_name(i[1][1], i[1][3], i[1][0], i[1][2], quantity, self.image, self.theme, self.imgID)
            else:
                quantity = nb
                self.data_pass_name(i[1][1], i[1][3], i[1][0], i[1][2], quantity, self.image, self.theme, self.imgID)
        log.debug(self.relic_list)
        return self.relic_list


ocr = OcrCheck(image_input)
ocr_data = ocr.ocr_loop()
pprint(ocr_data)