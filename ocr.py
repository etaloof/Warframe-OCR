import pytesseract
import cv2
import numpy as np
from PIL import Image
from spellcheck import SpellCheck


def spell_correction_ocr(string):
    spell_check_ocr = SpellCheck('ref/ref_words_ocr.txt')
    spell_check_ocr.check(string)
    return spell_check_ocr.correct().capitalize()


# Extract quality from the ocr result
def ocr_extract_quality(string):
    matchs = ("exceptionnelle", "impeccable", "eclatante", "exceptional", "flawless", "radiant")
    if any(s in string for s in matchs):
        return spell_correction_ocr(string.split("\n")[-1])
    else:
        return "Intacte"


# Extract era from the ocr result
def ocr_extract_era(string):
    if 'relique' in string:
        return string.split("\n")[0].split("relique")[1][:-2]
    if 'relic' in string:
        return string.split("relic")[0][:-2]


# Extract Name from the ocr result
def ocr_extract_name(string):
    if 'relique' in string:
        return string.split("\n")[0].split("relique")[1][-2:]
    if 'relic' in string:
        return string.split("relic")[0][-2:]


# Extract values from the ocr result
def extract_vals(text):
    p_string = text.casefold().rstrip()
    quality = ocr_extract_quality(p_string)
    era = ocr_extract_era(p_string)
    name = ocr_extract_name(p_string)
    return era, name, quality


# Check for specific sprite to see if the relic exist
def check_for_sign(img):
    precision = 0.96
    path_to_img = r'./relic_templatev2.png'
    path_to_mask = r'./relic_maskv2.png'
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


# Crop an area of a relic
def relicarea_crop(upper_y, downer_y, left_x, right_x, img):
    # upperY:downerY, LeftX:RightX
    cropped = img[upper_y:downer_y, left_x:right_x]
    return cropped


def data_pass_nb(pos1, pos2, pos3, pos4, image, theme):
    relic_raw = image
    cropped_img = relicarea_crop(pos1, pos2, pos3, pos4, relic_raw)
    greyed_image = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
    upscaled = cv2.resize(cropped_img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    if check_for_sign(greyed_image) >= 1:
        return False
    else:
        kernel = np.ones((1, 1), np.uint8)
        img = cv2.dilate(upscaled, kernel, iterations=1)
        kernelled = cv2.erode(img, kernel, iterations=1)
        ret, imgtresh = cv2.threshold(create_mask(theme, kernelled), 218, 255, cv2.THRESH_BINARY_INV)
        tessdata_dir_config = '--tessdata-dir "/home/Warframe-OCR/tessdata" -l Roboto --oem 1 -c tessedit_char_whitelist=Xx0123456789 get.images'
        text = pytesseract.image_to_string(imgtresh, config=tessdata_dir_config)
        return text.casefold()


# Detect the theme used in the UI screenshot
def get_theme(image):
    image = Image.fromarray(image)
    print('set theme')
    if image.load()[115, 86] == (102, 169, 190):
        return 'Virtuvian'
    if image.load()[115, 86] == (35, 31, 153):
        return 'Stalker'
    if image.load()[115, 86] == (255, 255, 255):
        return 'Ancient'
    if image.load()[115, 86] == (167, 159, 158):
        return 'Equinox'
    else:
        return 'Bad'


# Image processing for better detection after
def create_mask(theme, img):
    if theme == 'Virtuvian':
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_virtu = np.array([-3, 80, 80])
        upper_virtu = np.array([43, 255, 255])
        mask = cv2.inRange(hsv, lower_virtu, upper_virtu)
        return mask
    if theme == 'Stalker':
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_stalk = np.array([159, 80, 80])
        upper_stalk = np.array([199, 255, 255])
        mask = cv2.inRange(hsv, lower_stalk, upper_stalk)
        return mask
    if theme == 'Ancient':
        return img
    if theme == 'Equinox':
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_equi = np.array([107, 0, 0])
        upper_equi = np.array([127, 255, 255])
        mask = cv2.inRange(hsv, lower_equi, upper_equi)
        return mask


class OcrCheck:
    def __init__(self, image):
        self.image = image
        self.relic_list = []
        self.theme = get_theme(self.image)
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

    def data_pass_name(self, pos1, pos2, pos3, pos4, quantity, image, theme):
        relic_raw = image
        cropped_img = relicarea_crop(pos1, pos2, pos3, pos4, relic_raw)
        upscaled = cv2.resize(cropped_img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        kernel = np.ones((1, 1), np.uint8)
        img = cv2.dilate(upscaled, kernel, iterations=1)
        kernelled = cv2.erode(img, kernel, iterations=1)
        ret, imgtresh = cv2.threshold(create_mask(theme, kernelled), 218, 255, cv2.THRESH_BINARY_INV)
        tessdata_dir_config = '--tessdata-dir "/home/Warframe-OCR/tessdata" -l Roboto --oem 1 -c tessedit_char_whitelist=ABCDEFGHIKLMNOPQRSTUVWXYZabcdefghiklmnopqrstuvwxyz0123456789 get.images'
        text = pytesseract.image_to_string(imgtresh, config=tessdata_dir_config)
        self.relic_list.append(extract_vals(text) + (quantity,))

    def ocr_loop(self):
        for i in self.pos_list:
            nb = data_pass_nb(i[0][1], i[0][3], i[0][0], i[0][2], self.image, self.theme)
            if nb is False:
                pass
            elif nb == '':
                quantity = '1'
                self.data_pass_name(i[1][1], i[1][3], i[1][0], i[1][2], quantity, self.image, self.theme)
            else:
                quantity = nb[1:]
                self.data_pass_name(i[1][1], i[1][3], i[1][0], i[1][2], quantity, self.image, self.theme)
        return self.relic_list



