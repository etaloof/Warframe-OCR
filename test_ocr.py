import pytesseract
import cv2
from PIL import Image
from PIL import ImageFilter
from utils import *
import numpy as np

pos_list = [((100, 204, 126, 223), (101, 340, 259, 365))]


def relicarea_crop(upper_y, downer_y, left_x, right_x):
    relic_raw = cv2.imread('relic.png')
    # upperY:downerY, LeftX:RightX
    cropped = relic_raw[upper_y:downer_y, left_x:right_x]
    return cropped


def data_pass_name(pos1, pos2, pos3, pos4):
    # Binarize the screenshot
    image_to_binarize = relicarea_crop(pos1, pos2, pos3, pos4)
    greyed_image = cv2.cvtColor(image_to_binarize, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("temp_grey.jpg", greyed_image)

    resized_image = cv2.resize(greyed_image, None, fx=1.0, fy=1.0, interpolation=cv2.INTER_CUBIC)

    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(resized_image, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)
    cv2.imwrite('testeuh.jpg', img)

    # Find text via PyTesseract
    pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract"
    tessdata_dir_config = '--tessdata-dir "C:\\Users\\PRAN152\\Documents\\-- Perso --\\GitHub\\Warframe-OCR\\tessdata" -l Roboto --oem 1 '
    text = pytesseract.image_to_string(img, config=tessdata_dir_config)

    # corr_text = spell_correct(text)

    print(text)


def cycle_read():
    for i in pos_list:
        data_pass_name(i[1][1], i[1][3], i[1][0], i[1][2])
        data_pass_name(i[0][1], i[0][3], i[0][0], i[0][2])


if __name__ == '__main__':
    cycle_read()
