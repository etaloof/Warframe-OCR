import cv2
import cython

# Check pixel for tresholding
def check_pix(input_pix_clr, input_theme, color_treshold):
    e = [item for item in ui_color_list if item[3] == theme][0]
    if abs(input_pix_clr[2] - e[0]) < color_treshold and abs(input_pix_clr[1] - e[1]) < color_treshold and abs(input_pix_clr[0] - e[2]) < color_treshold:
        return True
    else:
        return False
            

@cython.boundscheck(False)
cpdef tresh(image, theme):
    h = image.shape[0] # Hauteur
    w = image.shape[1] # Largeur
    for y in range(0, h):
        for x in range(0, w):
            pix_crl = image[y, x]
            if check_pix(pix_crl, theme, 30) is True:
                image[y, x] = 0
            else:
                image[y, x] = 255
    
    return image