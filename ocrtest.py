import pytesseract
import cv2
import numpy
from PIL import Image, ImageFilter


def relicarea_crop():
    relic_raw = cv2.imread("relic.png")
    # out = cv2.rectangle(relic_raw, (97, 199), (264, 366), (0, 255, 0), 2)
    cropped = relic_raw[199:366, 97:264]
    return cropped


def get_data_from_screen():
    # Binarize the screenshot
    image_to_binarize = relicarea_crop()
    greyed_image = cv2.cvtColor(image_to_binarize, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("temp_grey.jpg", greyed_image)

    # Resize the screenshot
    image_to_resize = Image.open("temp_grey.jpg")
    basewidth = 167
    wpercent = (basewidth / float(image_to_resize.size[0]))
    hsize = int((float(image_to_resize.size[1]) * float(wpercent)))
    resized_image = image_to_resize.resize((basewidth, hsize), Image.BICUBIC)

    # Unsharp the image
    filtre = ImageFilter.UnsharpMask(6.8, 269, 0)
    unsharped_image = resized_image.filter(filtre)

    last = unsharped_image.convert("RGB")

    # Find text via PyTesseract
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract'
    tessdata_dir_config = '--tessdata-dir "C:\\Program Files (x86)\\Tesseract-OCR\\tessdata" -l test --oem 0 '
    text = pytesseract.image_to_string(last, config=tessdata_dir_config)
    print(text)


if __name__ == '__main__':
    get_data_from_screen()
