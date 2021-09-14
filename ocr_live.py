from screen_capture import mss, Screenshots
from ocr_local import *

spell_correction_ocr(None, None, set_selected=1)


def generate_overlay(image, ocr_check):
    for ((kind, pos1, pos2, pos3, pos4), img) in sorted(ocr_check.debug_images.items()):
        if kind == 'name':
            img = cv2.resize(img, None, img.shape[2:], 0.5, 0.5)
        elif kind == 'nb':
            img = np.hstack((255 - img[0], cv2.resize(img[1], None, img[1].shape[2:], 0.5, 0.5)))
            pos4 = pos2 + img.shape[0]
            pos3 = pos1 + img.shape[1]
        image[pos2:pos4, pos1:pos3] = img

    image = cv2.resize(image, None, image.shape[2:], 0.6, 0.6)
    return image


cv2.namedWindow('overlay', cv2.WINDOW_AUTOSIZE)
cv2.moveWindow('overlay', 1920, 0)

tessdata_dir = 'tessdata/'
with mss.mss() as sct, TesserocrPool(tessdata_dir, 'Roboto', psm=PSM.SINGLE_BLOCK, oem=OEM.LSTM_ONLY) as tess:
    screenshots = Screenshots(sct)
    while True:
        start = time.time()

        image_input = cv2.imread('ressources/100.png')  # screenshots.take_screenshot()

        if image_input.shape[:2] == (900, 1600):
            image_input = cv2.resize(image_input, (1920, 1080))
        ocr = RustyOcrCheck(tess, image_input)
        ocr_data = ocr.ocr_loop()

        end = time.time()

        pprint(ocr_data)
        print(f'latency: {int((end - start) * 1000)}ms')

        cv2.imshow('overlay', generate_overlay(image_input, ocr))
        cv2.waitKey(1)
