import pytesseract
import cv2
import numpy as np
from PIL import Image
from spellcheck import SpellCheck
import uuid
import logging
import shutil
import names
from random import randint
import re

# Enable logging
log = logging.getLogger("BlackBot_log")
log.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(message)s", "%Y-%m-%d %H:%M:%S")
console.setFormatter(formatter)
log.addHandler(console)

fh = logging.FileHandler('Warframe-Bot.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s.%(msecs)03d - %(name)s:%(lineno)d - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
fh.setFormatter(formatter)
log.addHandler(fh)


class OcrCheck:
    def __init__(self, image):
        self.image = image
        self.relic_list = []
        self.theme = self.get_theme(self.image)
        self.imgID = names.get_last_name()
        # Ecart X entre les reliques d'une même ligne : 218, y : 201
        # Block1 = Nombre, Block2 = Nom | LeftX, UpperY, RightX, DownerY
        self.pos_list = [((99, 204, 139, 226), (101, 319, 259, 365)),
                         ((317, 204, 357, 226), (318, 319, 477, 365)),
                         ((534, 204, 574, 226), (536, 319, 695, 365)),
                         ((750, 204, 790, 226), (747, 319, 906, 365)),
                         ((966, 204, 1006, 226), (965, 319, 1124, 365)),

                         ((99, 407, 139, 429), (101, 522, 259, 568)),
                         ((317, 407, 357, 429), (318, 522, 477, 568)),
                         ((534, 407, 574, 429), (536, 522, 695, 568)),
                         ((750, 407, 790, 429), (747, 522, 906, 568)),
                         ((966, 407, 1006, 429), (965, 522, 1124, 568)),

                         ((99, 609, 139, 631), (101, 724, 259, 770)),
                         ((317, 609, 357, 631), (318, 724, 477, 770)),
                         ((534, 609, 574, 631), (536, 724, 695, 770)),
                         ((750, 609, 790, 631), (747, 724, 906, 770)),
                         ((966, 609, 1006, 631), (965, 724, 1124, 770)),

                         ((99, 813, 139, 832), (101, 928, 259, 974)),
                         ((317, 813, 357, 832), (318, 928, 477, 974)),
                         ((534, 813, 574, 832), (536, 928, 695, 974)),
                         ((750, 813, 790, 832), (747, 928, 906, 974)),
                         ((966, 813, 1006, 832), (965, 928, 1124, 974))
                         ]
                         
    # Try to correct mistakes
    def spell_correction_ocr(self, string, corr_model):
        spell_check_ocr = SpellCheck(corr_model)
        spell_check_ocr.check(string)
        return spell_check_ocr.correct().strip().capitalize()

    # Extract quality from the ocr result (NO SPELLCHECK FOR NOW)
    def ocr_extract_quality(self, string):
        if any(s in string for s in ['exceptionnelle', 'éxceptionnelle', 'exceptional']):
            return 'Exceptionnelle'
        if any(s in string for s in ['eclatante', 'éclatante', 'radiant']):
            return 'Eclatante'
        if any(s in string for s in ['impeccable', 'flawless']):
            return 'Impeccable'
        else:
            return 'Intacte'
            
    # Extract era from the ocr result (WITH SPELLCHECK)
    def ocr_extract_era(self, string):
        rel_eng = self.spell_correction_ocr(' '.join(string.split(" ")[2:])[:5].lower(), 'ref/ref_1_ocr.txt').lower()
        rel_fr = self.spell_correction_ocr(string.split(" ")[0].lower(), 'ref/ref_1_ocr.txt').lower()
        print(rel_eng)
        if 'relique' in rel_fr:
            if 'axi' in string:
                return 'Axi'
            if 'neo' in string:
                return 'Neo'
            if 'meso' in string:
                return 'Meso'
            if 'lith' in string:
                return 'Lith'
        if 'relic' in rel_eng:
            if 'axi' in string:
                return 'Axi'
            if 'neo' in string:
                return 'Neo'
            if 'meso' in string:
                return 'Meso'
            if 'lith' in string:
                return 'Lith'
                
    # Extract Name from the ocr result (NO SPELLCHECK)
    def ocr_extract_name(self, string):
        rel_eng = self.spell_correction_ocr(' '.join(string.split(" ")[2:])[:5].lower(), 'ref/ref_1_ocr.txt').lower()
        rel_fr = self.spell_correction_ocr(string.split(" ")[0].lower(), 'ref/ref_1_ocr.txt').lower()
        if 'relique' in rel_fr:
            return ' '.join(string.split(" ")[2:])[:3].capitalize().rstrip()
        if 'relic' in rel_eng:
            return string.split(" ")[1][:3].capitalize().rstrip()
            
    # Extract values from the ocr result
    def extract_vals(self, text):
        p_string = text.casefold().rstrip()
        
        if self.ocr_extract_quality(p_string) is not None:
            quality = self.ocr_extract_quality(p_string)
        else:
            quality = 'OcrError'
            
        if self.ocr_extract_era(p_string) is not None:
            era = self.ocr_extract_era(p_string)
        else:
            era = 'OcrError'
            
        if self.ocr_extract_name(p_string) is not None:
            name = self.ocr_extract_name(p_string)
        else:
            name = 'OcrError'
            
        return era, name, quality

    # Check for specific sprite to see if the relic exist
    def check_for_sign(self, img):
        precision = 0.96
        path_to_img = r'./relic_template.png'
        path_to_mask = r'./relic_mask.png'
        template = cv2.imread(path_to_img, 0)
        mask = cv2.imread(path_to_mask, 0)
        w, h = template.shape[::-1]
        res = cv2.matchTemplate(img, template, cv2.TM_CCORR_NORMED, mask=mask)
        loc = np.where(res >= precision)
        count = 0
        for pt in zip(*loc[::-1]):  # Swap columns and rows
            cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
            count = count + 1
        return count
        
    # Crop an area of a relic
    def relicarea_crop(self, upper_y, downer_y, left_x, right_x, img):
        # upperY:downerY, LeftX:RightX
        cropped = img[upper_y:downer_y, left_x:right_x]
        return cropped
    
    # Detect the theme used in the UI screenshot
    # Themes : High Constrast - Equinox - Virtuvian - Ancient - Baruuk - Corpus - Fortuna - Grineer - Lotus - Dark lotus - Nidus - Orokin - Stalker - Tenno
    # Supported : Virtuvian - Stalker - Ancient (Bugged) - Equinox
    def get_theme(self, image):
        image = Image.fromarray(image)
        if image.load()[115, 86] == (102, 169, 190):
            return 'Virtuvian'
        if image.load()[115, 86] == (35, 31, 153):
            return 'Stalker'
        if image.load()[115, 86] == (255, 255, 255):
            return 'Le theme ANCIENT n\'est pas supporté pour l\'instant.' # Ancient
        if image.load()[115, 86] == (167, 159, 158):
            return 'Equinox'
        if image.load()[115, 86] == (192, 105, 57):
            return 'Fortuna'
        else:
            return 'Ce theme n\'est pas supporté pour l\'instant.'
            
    # Image processing for better detection after
    def create_mask(self, theme, img):
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
            
    def data_pass_name(self, pos1, pos2, pos3, pos4, quantity, image, theme, id):
        # Generate rID
        rid = str(randint(100, 999))
        # Taking the full image -> cropping -> upscaling -> dilate / erode -> ?
        relic_raw = image
        cropped_img = self.relicarea_crop(pos1, pos2, pos3, pos4, relic_raw)
        upscaled = cv2.resize(cropped_img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        
        # Write the raw img
        cv2.imwrite('test_img_ocr/brut/' + 'name_' + rid + '.jpg', upscaled) # BRUT
        
        # kernel = np.ones((1, 1), np.uint8)
        # erode = cv2.erode(upscaled, kernel, iterations=1)
        # dilate = cv2.dilate(erode, kernel, iterations=1)
        # cv2.imwrite('test_img_ocr/after_opening/' + 'name_' + str(uuid.uuid1()) + '.jpg', dilate) # AFTER_OPENING
        
        # Treshold the img with the mask
        ret, imgtresh = cv2.threshold(self.create_mask(theme, upscaled), 218, 255, cv2.THRESH_BINARY_INV)
        # Write the mask img
        cv2.imwrite('test_img_ocr/mask/' + 'name_' + id + '_' + rid + '.jpg', self.create_mask(theme, upscaled)) # MASK
        # Write the mask applied img with treshold
        cv2.imwrite('test_img_ocr/after_masking/' + 'name_' + id + '_' + rid + '.jpg', imgtresh) # AFTER_MASKING
        # Actual OCR
        tessdata_dir_config = '--tessdata-dir "/home/Warframe-OCR/tessdata" -l Roboto --oem 1 --psm 6 get.images -c tessedit_char_blacklist=jJyY'
        textocr = pytesseract.image_to_string(imgtresh, config=tessdata_dir_config)
        # Write the pre-input tif
        tiffname = '/home/Warframe-OCR/test_img_ocr/tiffs/name_' + id + '_' + rid + '.tif'
        shutil.move("/home/Warframe-OCR/tessinput.tif", tiffname)
        # Write log for result
        log.debug('[' + id + '] ' + '[ Tesseract output for TEXT is : ' + textocr + ' ]') # DEBUG
        if textocr == '':
            pass
        else:
            stripocr = textocr.replace('\n', ' ')
            self.relic_list.append(self.extract_vals(stripocr) + (quantity,))

    def data_pass_nb(self, pos1, pos2, pos3, pos4, image, theme, id):
        # Generate rID
        rid = str(randint(100, 999))
        
        relic_raw = image
        cropped_img = self.relicarea_crop(pos1, pos2, pos3, pos4, relic_raw)
        greyed_image = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
        upscaled = cv2.resize(cropped_img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        if self.check_for_sign(greyed_image) >= 1:
            return False
        else:
            log.debug('[' + id + '] ' + '[ Theme used is : ' + theme + ' ]')  # DEBUG
            
            # kernel = np.ones((1, 1), np.uint8)
            # erode = cv2.erode(upscaled, kernel, iterations=1)
            # dilate = cv2.dilate(erode, kernel, iterations=1)
            
            ret, imgtresh = cv2.threshold(self.create_mask(theme, upscaled), 218, 255, cv2.THRESH_BINARY_INV)
            
            cv2.imwrite('test_img_ocr/number/' + 'number_' + id + '_' + rid + '.jpg', imgtresh)
            
            tessdata_dir_config = '--tessdata-dir "/home/Warframe-OCR/tessdata" -l Roboto --psm 6 --oem 1 get.images'

            text = pytesseract.image_to_string(imgtresh, config=tessdata_dir_config)
            
            # Write the pre-input tif
            tiffname = '/home/Warframe-OCR/test_img_ocr/tiffs/nb_' + id + '_' + rid + '.tif'
            shutil.move("/home/Warframe-OCR/tessinput.tif", tiffname)
            
            log.debug('[' + id + '] ' + '[ Tesseract output for NB is : ' + text + ' ]')
            
            corrected_nbr = re.sub("[^0-9]", "", text)
            
            return corrected_nbr.casefold()
        
    def ocr_loop(self):
        for i in self.pos_list:
            if self.theme not in ['Virtuvian', 'Stalker', 'Fortuna', 'Equinox']:
                return self.theme
            else :
                nb = self.data_pass_nb(i[0][1], i[0][3], i[0][0], i[0][2], self.image, self.theme, self.imgID)
                if nb is False:
                    pass
                elif nb == '':
                    quantity = '1'
                    self.data_pass_name(i[1][1], i[1][3], i[1][0], i[1][2], quantity, self.image, self.theme, self.imgID)
                else:
                    quantity = nb
                    self.data_pass_name(i[1][1], i[1][3], i[1][0], i[1][2], quantity, self.image, self.theme, self.imgID)
        log.debug(self.relic_list)
        return self.relic_list