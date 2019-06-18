import pytesseract
import cv2
from PIL import Image
from PIL import ImageFilter
from utils import *
import numpy as np
from spellcheck import SpellCheck
spell_check = SpellCheck('ref/ref_words_ocr.txt')

# Ecart X entre les reliques d'une même ligne : 218, y : 201
# Block1 = Nombre, Block2 = Nom | LeftX, UpperY, RightX, DownerY
pos_list = [((100, 204, 126, 223), (101, 319, 259, 365)),
            ((318, 204, 344, 223), (318, 319, 477, 365)),
            ((536, 204, 562, 223), (536, 319, 695, 365)),
            ((754, 204, 780, 223), (754, 319, 913, 365)),
            ((972, 204, 998, 223), (972, 319, 1131, 365)),

            ((100, 405, 126, 424), (101, 520, 259, 566)),
            ((318, 405, 344, 424), (318, 520, 477, 566)),
            ((536, 405, 562, 424), (536, 520, 695, 566)),
            ((754, 405, 780, 424), (754, 520, 913, 566)),
            ((972, 405, 998, 424), (972, 520, 1131, 566)),

            ((100, 606, 126, 625), (101, 721, 259, 767)),
            ((318, 606, 344, 625), (318, 721, 477, 767)),
            ((536, 606, 562, 625), (536, 721, 695, 767)),
            ((754, 606, 780, 625), (754, 721, 913, 767)),
            ((972, 606, 998, 625), (972, 721, 1131, 767)),

            ((100, 807, 126, 826), (101, 922, 259, 968)),
            ((318, 807, 344, 826), (318, 922, 477, 968)),
            ((536, 807, 562, 826), (536, 922, 695, 968)),
            ((754, 807, 780, 826), (754, 922, 913, 968)),
            ((972, 807, 998, 826), (972, 922, 1131, 968))
            ]


def relicarea_crop(upper_y, downer_y, left_x, right_x):
    relic_raw = cv2.imread('relic.png')
    # upperY:downerY, LeftX:RightX
    cropped = relic_raw[upper_y:downer_y, left_x:right_x]
    return cropped


def data_pass(pos1, pos2, pos3, pos4):
    # Binarize the screenshot
    image_to_binarize = relicarea_crop(pos1, pos2, pos3, pos4)
    greyed_image = cv2.cvtColor(image_to_binarize, cv2.COLOR_BGR2GRAY)

    resized_image = cv2.resize(greyed_image, None, fx=1.0, fy=1.0, interpolation=cv2.INTER_CUBIC)

    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(resized_image, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)


    # Find text via PyTesseract
    char_white = "C:\\Users\\Demokdawa\\Documents\\PythonProjects\\Warframe-OCR\\tessdata\\configs\\letters.txt"
    pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract"
    # tessdata_dir_config = '--tessdata-dir "C:\\Users\\PRAN152\\Documents\\-- Perso --\\GitHub\\Warframe-OCR\\tessdata" -l Roboto --oem 1 '
    tessdata_dir_config = '--tessdata-dir "C:\\Users\\Demokdawa\\Documents\\PythonProjects\\Warframe-OCR\\tessdata" -l Roboto --oem 3  -c tessedit_char_whitelist=ABCDEFGHIKLMNOPQRSTUVWXYZabcdefghiklmnopqrstuvwxyz0123456789'
    text = pytesseract.image_to_string(img, config=tessdata_dir_config)

    spell_check.check(text)
    cv2.imwrite('test_img_ocr/' + spell_check.correct() + '.jpg', img)
    print(spell_check.correct())


def cycle_read():
    for i in pos_list:
        data_pass(i[1][1], i[1][3], i[1][0], i[1][2])
        data_pass(i[0][1], i[0][3], i[0][0], i[0][2])


if __name__ == '__main__':
    cycle_read()
