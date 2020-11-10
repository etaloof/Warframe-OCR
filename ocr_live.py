from screen_capture import mss, Screenshots
from ocr_local import *

tessdata_dir = 'tessdata/'
with mss.mss() as sct, PyTessBaseAPI(tessdata_dir, 'Roboto', psm=PSM.SINGLE_BLOCK, oem=OEM.LSTM_ONLY) as tess:
    screenshots = Screenshots(sct)
    while True:
        start = time.time()

        image_input = screenshots.take_screenshot()

        if image_input.shape[:2] == (900, 1600):
            image_input = cv2.resize(image_input, (1920, 1080))
        ocr = OcrCheck(tess, image_input)
        ocr_data = ocr.ocr_loop()

        end = time.time()

        pprint(ocr_data)
        print(f'latency: {int((end-start) * 1000)}ms')
