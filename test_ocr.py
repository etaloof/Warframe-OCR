import pytesseract
import cv2
import numpy as np
from spellcheck import SpellCheck

spell_check = SpellCheck('ref/ref_words_ocr.txt')

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


def check_for_sign(img):
    precision = 0.95
    path_to_img = r'./relic_template.png'
    path_to_mask = r'./relic_mask.png'
    template = cv2.imread(path_to_img, 0)
    mask = cv2.imread(path_to_mask, 0)
    w, h = template.shape[::-1]
    res = cv2.matchTemplate(img, template, cv2.TM_CCORR_NORMED, mask=mask)
    print(template.shape)
    loc = np.where(res >= precision)
    count = 0
    for pt in zip(*loc[::-1]):  # Swap columns and rows
        cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
        count = count + 1
    cv2.imwrite('Result.png',img)
    print(loc)
    print(count)


def ocr_correct_pass2(string):
    if 'hfeo' in string:
        return string.replace('hfeo', 'meso', 1)
    if 'm so' in string:
        return string.replace('m so', 'meso', 1)
    else:
        return string


def ocr_split(string):
    if 'relique' in string:
        return 'relique' + string.split("relique")[1]
    if 'relic' in string:
        return 'relic ' + string.split("relic")[0]


def ocr_correc_pass1(string):
    if string[-1] == "t":
        return string[:-1] + "1"
    if string[-1] == "z":
        return string[:-1] + "2"
    else:
        return string


def relicarea_crop(upper_y, downer_y, left_x, right_x, img):
    # upperY:downerY, LeftX:RightX
    cropped = img[upper_y:downer_y, left_x:right_x]
    return cropped


def data_pass_name(pos1, pos2, pos3, pos4):
    # Binarize the screenshot
    relic_raw = cv2.imread('relic2.png')

    cropped_img = relicarea_crop(pos1, pos2, pos3, pos4, relic_raw)

    resized_image = cv2.resize(cropped_img, None, fx=1, fy=1, interpolation=cv2.INTER_LINEAR)

    greyed_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)

    print(check_for_sign(greyed_image))

    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(greyed_image, kernel, iterations=1)
    kernelled = cv2.erode(img, kernel, iterations=1)

    # Find text via PyTesseract
    pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract"
    tessdata_dir_config = '--tessdata-dir "C:\\Users\\PRAN152\\Documents\\-- Perso --\\GitHub\\Warframe-OCR\\tessdata" -l Roboto --oem 3 -c tessedit_char_whitelist=ABCDEFGHIKLMNOPQRSTUVWZabcdefghiklmnopqrstuvwz0123456789'
    # tessdata_dir_config = '--tessdata-dir "C:\\Users\\Demokdawa\\Documents\\PythonProjects\\Warframe-OCR\\tessdata" -l Roboto --oem 3  -c tessedit_char_whitelist=ABCDEFGHIKLMNOPQRSTUVWXYZabcdefghiklmnopqrstuvwxyz0123456789'
    text = pytesseract.image_to_string(kernelled, config=tessdata_dir_config)

    spell_check.check(text.casefold())
    # cv2.imwrite('test_img_ocr/' + spell_check.correct() + '.jpg', kernelled)
    print(ocr_correc_pass1(ocr_correct_pass2(ocr_split(spell_check.correct()))))


def data_pass_nb(pos1, pos2, pos3, pos4):
    # Binarize the screenshot
    relic_raw = cv2.imread('relic3.png')

    cropped_img = relicarea_crop(pos1, pos2, pos3, pos4, relic_raw)

    resized_image = cv2.resize(cropped_img, None, fx=1, fy=1, interpolation=cv2.INTER_LINEAR)

    greyed_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)

    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(greyed_image, kernel, iterations=1)
    kernelled = cv2.erode(img, kernel, iterations=1)

    # Find text via PyTesseract
    pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract"
    tessdata_dir_config = '--tessdata-dir "C:\\Users\\PRAN152\\Documents\\-- Perso --\\GitHub\\Warframe-OCR\\tessdata" -l Roboto --oem 3 -c tessedit_char_whitelist=Xx0123456789'
    # tessdata_dir_config = '--tessdata-dir "C:\\Users\\Demokdawa\\Documents\\PythonProjects\\Warframe-OCR\\tessdata" -l Roboto --oem 3  -c tessedit_char_whitelist=ABCDEFGHIKLMNOPQRSTUVWXYZabcdefghiklmnopqrstuvwxyz0123456789'
    text = pytesseract.image_to_string(kernelled, config=tessdata_dir_config)

    spell_check.check(text.casefold())
    # cv2.imwrite('test_img_ocr/' + spell_check.correct() + '.jpg', kernelled)
    print(spell_check.correct())


def cycle_read():
    for i in pos_list:
        nb = data_pass_nb(i[0][1], i[0][3], i[0][0], i[0][2])
        if nb is True:
            pass
        data_pass_name(i[1][1], i[1][3], i[1][0], i[1][2])


if __name__ == '__main__':
    cycle_read()
