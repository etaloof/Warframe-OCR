import pytesseract
import cv2
import numpy as np
from spellcheck import SpellCheck

spell_check = SpellCheck('ref/ref_words_ocr.txt')

relic_list = []

# Ecart X entre les reliques d'une même ligne : 218, y : 201
# Block1 = Nombre, Block2 = Nom | LeftX, UpperY, RightX, DownerY
pos_list = [((99, 204, 139, 226), (101, 319, 259, 365)),
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


def purify_result(text):
    spell_check.check(text.casefold())
    p_string = spell_check.correct()
    p_string = ocr_split(p_string)
    p_string = p_string.rstrip()
    p_string = ocr_correct_pass1(p_string)
    p_string = ocr_correct_pass2(p_string)
    return p_string


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


def ocr_correct_pass2(string):
    if 'm so' in string:
        return string.replace('m so', 'meso', 1)
    if 'me so' in string:
        return string.replace('me so', 'meso', 1)
    if 'mcsd' in string:
        return string.replace('mcsd', 'meso', 1)
    else:
        return string


def ocr_split(string):
    if 'relique' in string:
        return 'relique' + string.split("relique")[1]
    if 'relic' in string:
        return 'relic ' + string.split("relic")[0]


def ocr_correct_pass1(string):
    if string[-1] == "t":
        return string[:-1] + "1"
    if string[-1] == "z":
        return string[:-1] + "2"
    if string[-1] == "s":
        return string[:-1] + "8"
    if string[-1] == "g":
        return string[:-1] + "8"
    else:
        return string


def relicarea_crop(upper_y, downer_y, left_x, right_x, img):
    # upperY:downerY, LeftX:RightX
    cropped = img[upper_y:downer_y, left_x:right_x]
    return cropped


def data_pass_name(pos1, pos2, pos3, pos4, quantity):
    relic_raw = cv2.imread('relic6.png')
    cropped_img = relicarea_crop(pos1, pos2, pos3, pos4, relic_raw)
    greyed_image = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(greyed_image, kernel, iterations=1)
    kernelled = cv2.erode(img, kernel, iterations=1)
    # Find text via PyTesseract
    pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract"
    tessdata_dir_config = '--tessdata-dir "C:\\Users\\PRAN152\\Documents\\-- Perso --\\GitHub\\Warframe-OCR\\tessdata" -l Roboto --oem 1 -c tessedit_char_whitelist=ABCDEFGHIKLMNOPQRSTUVWZabcdefghiklmnopqrstuvwz123456789'
    # tessdata_dir_config = '--tessdata-dir "C:\\Users\\Demokdawa\\Documents\\PythonProjects\\Warframe-OCR\\tessdata" -l Roboto-ori --oem 3  -c tessedit_char_whitelist=ABCDEFGHIKLMNOPQRSTUVWXYZabcdefghiklmnopqrstuvwxyz0123456789'
    text = pytesseract.image_to_string(kernelled, config=tessdata_dir_config)
    # relic_list.append(ocr_correc_pass1(ocr_correct_pass2(ocr_split(spell_check.correct())) + quantity))
    cv2.imwrite('test_img_ocr/' + purify_result(text) + '.jpg', kernelled)
    print(purify_result(text) + ' ' + quantity)
    # print(ocr_correc_pass1(ocr_correct_pass2(ocr_split(spell_check.correct()))) + ' ' + quantity)


def data_pass_nb(pos1, pos2, pos3, pos4):
    relic_raw = cv2.imread('relic6.png')

    cropped_img = relicarea_crop(pos1, pos2, pos3, pos4, relic_raw)

    greyed_image = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)

    if (check_for_sign(greyed_image)) >= 1:
        return False
    else:
        kernel = np.ones((1, 1), np.uint8)
        img = cv2.dilate(greyed_image, kernel, iterations=1)
        kernelled = cv2.erode(img, kernel, iterations=1)
        # Find text via PyTesseract
        pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract"
        tessdata_dir_config = '--tessdata-dir "C:\\Users\\PRAN152\\Documents\\-- Perso --\\GitHub\\Warframe-OCR\\tessdata" -l Roboto --oem 1 -c tessedit_char_whitelist=Xx0123456789'
        # tessdata_dir_config = '--tessdata-dir "C:\\Users\\Demokdawa\\Documents\\PythonProjects\\Warframe-OCR\\tessdata" -l Roboto-ori2 --oem 3  -c tessedit_char_whitelist=ABCDEFGHIKLMNOPQRSTUVWXYZabcdefghiklmnopqrstuvwxyz0123456789'
        text = pytesseract.image_to_string(kernelled, config=tessdata_dir_config)
        spell_check.check(text.casefold())
        return spell_check.correct()


def ocr_loop():
    for i in pos_list:
        nb = data_pass_nb(i[0][1], i[0][3], i[0][0], i[0][2])
        if nb is False:
            print('Relique inexistante')
        elif nb == '':
            quantity = '1'
            data_pass_name(i[1][1], i[1][3], i[1][0], i[1][2], quantity)
        else:
            quantity = nb[1:]
            data_pass_name(i[1][1], i[1][3], i[1][0], i[1][2], quantity)


if __name__ == '__main__':
    ocr_loop()
