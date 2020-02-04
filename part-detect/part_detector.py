import pytesseract
import cv2
import numpy as np
import shutil


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
    if theme == 'Fortuna':
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_equi = np.array([80, 80, 84])
        upper_equi = np.array([120, 199, 255])
        mask = cv2.inRange(hsv, lower_equi, upper_equi)
        return mask


file = 'theme_source.png'
image = cv2.imread(file)

upscaled = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

cv2.imwrite('/home/Warframe-OCR/part-detect/raw.jpg', upscaled)

ret, imgtresh = cv2.threshold(create_mask('Virtuvian', upscaled), 218, 255, cv2.THRESH_BINARY_INV)

cv2.imwrite('/home/Warframe-OCR/part-detect/mask.jpg', create_mask('Virtuvian', upscaled))

cv2.imwrite('/home/Warframe-OCR/part-detect/after_masking/after-mask.jpg', imgtresh)

tessdata_dir_config = '--tessdata-dir "/home/Warframe-OCR/tessdata" -l Roboto --oem 1 --psm 6 get.images'
textocr = pytesseract.image_to_string(imgtresh, config=tessdata_dir_config)
tiffname = '/home/Warframe-OCR/part-detect/test.tif'
shutil.move("/home/Warframe-OCR/part-detect/tessinput.tif", tiffname)

print(textocr)
