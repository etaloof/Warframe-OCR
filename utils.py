from spellcheck import SpellCheck
from scrap import update_vault_list
from ocr import OcrCheck
import numpy as np
import cv2
import requests

# Initialize ##################################################################################

v_relic_list = update_vault_list()

# Define reference file for Spellchecking
# spell_check = SpellCheck('ref/ref_words.txt')
spell_check = SpellCheck('ref/ref_words.txt')

# Define references files to use for Warframe Data
Era_file = 'ref/ref_era.txt'
Lith_file = 'ref/ref_lith.txt'
Meso_file = 'ref/ref_meso.txt'
Neo_file = 'ref/ref_neo.txt'
Axi_file = 'ref/ref_axi.txt'
Quality_file = 'ref/ref_quality.txt'
Ressources_file = 'ref/ref_ressources.txt'


# Parse references files to lists
def parse_ref_files(file):
    ref_list = []
    with open(file, "r") as fileHandler:
        for line in fileHandler:
            ref_list.append(line.strip())
    return ref_list


# Read references files for Warframe Data
ref_list_era = parse_ref_files(Era_file)
ref_list_lith = parse_ref_files(Lith_file)
ref_list_meso = parse_ref_files(Meso_file)
ref_list_neo = parse_ref_files(Neo_file)
ref_list_axi = parse_ref_files(Axi_file)
ref_list_quality = parse_ref_files(Quality_file)
ref_list_ressources = parse_ref_files(Ressources_file)


# Check if command args exists in Warframe for "Era", "Quality" and "Name"
def syntax_check_pass(arg1, arg2, arg3):
    # Check for Era
    if arg1 not in ref_list_era:
        return 'Cette ère de relique n\'existe pas ! (' + arg1 + ')'
    else:
        # Check for Name
        if arg1 == 'Lith':
            if arg2 not in ref_list_lith:
                return 'Cette relique n\'existe pas en Lith ! (' + arg2 + ')'
            else:
                if arg3 not in ref_list_quality:
                    return 'Cette qualité de relique n\'existe pas ! (' + arg3 + ')'
                else:
                    return True
        if arg1 == 'Meso':
            if arg2 not in ref_list_meso:
                return 'Cette relique n\'existe pas en Meso ! (' + arg2 + ')'
            else:
                if arg3 not in ref_list_quality:
                    return 'Cette qualité de relique n\'existe pas ! (' + arg3 + ')'
                else:
                    return True
        if arg1 == 'Neo':
            if arg2 not in ref_list_neo:
                return 'Cette relique n\'existe pas en Neo ! (' + arg2 + ')'
            else:
                if arg3 not in ref_list_quality:
                    return 'Cette qualité de relique n\'existe pas ! (' + arg3 + ')'
                else:
                    return True
        if arg1 == 'Axi':
            if arg2 not in ref_list_axi:
                return 'Cette relique n\'existe pas en Axi ! (' + arg2 + ')'
            else:
                if arg3 not in ref_list_quality:
                    return 'Cette qualité de relique n\'existe pas ! (' + arg3 + ')'
                else:
                    return True


# Check ressource syntax
def syntax_check_ressource(arg):
    if arg not in ref_list_ressources:
        return 'Cette ressource n\'existe pas !'
    else:
        return True


# Change string "tést" to "Test"
def capit_arg(string):
    return string.unidecode.capitalize()


# Change "test#0003" to "test"
def clean_disctag(name):
    sep = '#'
    rest = name.split(sep, 1)[0]
    return rest


# Try to correct spelling for commands, and translate english to french for "Quality" arg
def spell_correct(string):
    spell_check.check(string)
    if spell_check.correct().capitalize() == 'Intact':
        return 'Intacte'
    if spell_check.correct().capitalize() == 'Exceptional':
        return 'Exceptionnelle'
    if spell_check.correct().capitalize() == 'Flawless':
        return 'Impeccable'
    if spell_check.correct().capitalize() == 'Radiant':
        return 'Eclatante'
    else:
        return spell_check.correct().capitalize()


# Check if number of relic input by command is too high
def number_check(a4):
    if a4 > 100:
        return False
    else:
        return True


# Check if relic is vaulted
def is_vaulted(a1, a2):
    if a1 + ' ' + a2 in v_relic_list:
        return '**Vaulted**'
    else:
        return 'Unvaulted'


# Get the image from discord url
def image_from_url(url):
    url_response = requests.get(url, stream=True)
    nparr = np.frombuffer(url_response.content, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image


# Get image size
def check_image_size(image):
    height = image.shape[0]
    width = image.shape[1]
    return width, height


# Check if res is good, and start ocr process
def process_image(image):
    if check_image_size(image) == (1920, 1080):
        ocr = OcrCheck(image)
        message = ''
        for i in ocr.ocr_loop():
            # message += str('Relique X' + i[3] + ' ' + i[0] + ' ' + i[1] + ' ' + i[2] + '\n')
            message += str(i + '\n')
        return message
    else:
        return 'Le screenshot n\'est pas a la bonne résolution !'


