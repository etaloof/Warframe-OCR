from cv2.cv2 import WINDOW_NORMAL, WINDOW_AUTOSIZE

from screen_capture import mss, Screenshots
from ocr_local import *


def generate_overlay(image, ocr_check):
    for ((kind, pos1, pos2, pos3, pos4), img) in sorted(ocr_check.debug_images.items()):
        offset_y = offset_x = 0
        if kind == 'name':
            offset_y = pos2 - pos1
            img = cv2.resize(img, None, img.shape[2:], 0.5, 0.5)
        elif kind == 'nb':
            offset_x = pos4 - pos3
            img = 255 - img
        image[pos1 + offset_y:pos2 + offset_y, pos3 + offset_x:pos4 + offset_x] = img

    image = cv2.resize(image, None, image.shape[2:], 0.6, 0.6)
    return image


cv2.namedWindow('overlay', WINDOW_AUTOSIZE)
cv2.moveWindow('overlay', 1600, 0)

tessdata_dir = 'tessdata/'
with mss.mss() as sct, PyTessBaseAPI(tessdata_dir, 'Roboto', psm=PSM.SINGLE_BLOCK, oem=OEM.LSTM_ONLY) as tess:
    screenshots = Screenshots(sct)
    while True:
        start = time.time()

        image_input = cv2.imread('ressources/100.png')  # screenshots.take_screenshot()

        if image_input.shape[:2] == (900, 1600):
            image_input = cv2.resize(image_input, (1920, 1080))
        ocr = OcrCheck(tess, image_input)
        ocr_data = ocr.ocr_loop()

        end = time.time()

        pprint(ocr_data)
        print(f'latency: {int((end - start) * 1000)}ms')

        cv2.imshow('overlay', generate_overlay(image_input, ocr))
        cv2.waitKey(1)
