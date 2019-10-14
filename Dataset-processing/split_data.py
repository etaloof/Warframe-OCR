import os
import cv2

path = "./source"

# Get image size
def check_image_size(image):
    height = image.shape[0]
    width = image.shape[1]
    return width, height

for img in os.listdir(path):
    img_input = os.path.join(path, img)
    imgdata = cv2.imread(img_input)
    if check_image_size(imgdata) == (1920, 1080):
        os.mkdir(os.path.join(path, "img"))
    else:
        print("Erreur de la résolution image")