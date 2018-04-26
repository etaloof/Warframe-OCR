import pytesseract
import cv2
from PIL import Image, ImageFilter


def get_data_from_screen():
    # Binarize the screenshot
    image_to_binarize = cv2.imread("testnew.png")
    greyed_image = cv2.cvtColor(image_to_binarize, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("temp_grey.jpg", greyed_image)

    # Resize the screenshot
    image_to_resize = Image.open("temp_grey.jpg")
    basewidth = 1691
    wpercent = (basewidth / float(image_to_resize.size[0]))
    hsize = int((float(image_to_resize.size[1]) * float(wpercent)))
    resized_image = image_to_resize.resize((basewidth, hsize), Image.BICUBIC)

    # Unsharp the image
    filtre = ImageFilter.UnsharpMask(6.8, 269, 0)
    unsharped_image = resized_image.filter(filtre)

    # Find text via PyTesseract
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract'
    tessdata_dir_config = '--tessdata-dir "C:\\Users\\PRAN152\\PycharmProjects\\D3OCR\\tessdata" -l ' \
                          'fra+Exocet+ExocetBOLD --oem 1 '
    text = pytesseract.image_to_string(unsharped_image, config=tessdata_dir_config)
    print(text)


if __name__ == '__main__':
    get_data_from_screen()
