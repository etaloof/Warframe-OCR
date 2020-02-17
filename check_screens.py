input_file = "/ressources/1.png"
image = cv2.imread(input_file)

#UI-COLORS####################################################################################################

# RGB Format
ui_color_list = [
    (189, 168, 101, 'Virtuvian'),   # Vitruvian
    (150, 31, 35, 'Stalker'),       # Stalker 
    (238, 193, 105, 'Baruk'),       # Baruk
    (35, 200, 245, 'Corpus'),       # Corpus
    (57, 105, 192, 'Fortuna'),      # Fortuna
    (255, 189, 102, 'Grineer'),     # Grineer
    (36, 184, 242, 'Lotus'),        # Lotus
    (140, 38, 92, 'Nidus'),         # Nidus
    (20, 41, 29, 'Orokin'),         # Orokin
    (9, 78, 106, 'Tenno'),          # Tenno
    (2, 127, 217, 'High contrast'), # High contrast
    (255, 255, 255, 'Legacy'),      # Legacy
    (158, 159, 167, 'Equinox')      # Equinox
]

# Check ui theme from screenshot (Image Format : OPENCV)
def get_theme(image, color_treshold):
    input_clr = image[86, 115] # Y,X  RES-DEPENDANT
    for e in ui_color_list:
        if abs(input_clr[2] - e[0]) < color_treshold and abs(input_clr[1] - e[1]) < color_treshold and abs(input_clr[0] - e[2]) < color_treshold:
            return e[3]
        else:
            pass
    
##############################################################################################################

# Check ui theme from screenshot
def check_pix(input_pix_clr, input_theme, color_treshold):
    e = (189, 168, 101, 'Virtuvian')
    if abs(input_pix_clr[2] - e[0]) < color_treshold and abs(input_pix_clr[1] - e[1]) < color_treshold and abs(input_pix_clr[0] - e[2]) < color_treshold:
        return True
    else:
        return False
            
def tresh(image):
    h = image.shape[0] # Hauteur
    w = image.shape[1] # Largeur
    for y in range(0, h):
        for x in range(0, w):
            pix_crl = image[y, x]
            if check_pix(pix_crl, 'Stalker', 30) is True:
                image[y, x] = 0
            else:
                image[y, x] = 255
    
    return image
    
 
theme = get_theme(image, 30)
print(theme)