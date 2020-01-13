import os
import PySimpleGUI as sg
import itertools as it
from sys import exit
import cv2
import numpy as np


# Image processing for better detection after HSL format
def create_mask(theme, img):
    if theme == 'Virtuvian':
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_virtu = np.array([-3, 80, 80])
        upper_virtu = np.array([43, 255, 255])
        mask = cv2.inRange(hsv, lower_virtu, upper_virtu)
        cv2.imwrite('virtuv_mask.png', mask)
        return mask
    if theme == 'Stalker':
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_stalk = np.array([159, 80, 80])
        upper_stalk = np.array([199, 255, 255])
        mask = cv2.inRange(hsv, lower_stalk, upper_stalk)
        cv2.imwrite('stalker_mask.png', mask)
        return mask
    if theme == 'Ancient':
        return img
    if theme == 'Equinox':
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_equi = np.array([107, 0, 0])
        upper_equi = np.array([127, 255, 255])
        mask = cv2.inRange(hsv, lower_equi, upper_equi)
        cv2.imwrite('equinox_mask.png', mask)
        return mask
    if theme == 'Fortuna':
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_equi = np.array([108, 80, 80])
        upper_equi = np.array([152, 255, 255])
        mask = cv2.inRange(hsv, lower_equi, upper_equi)
        cv2.imwrite('fortuna_mask.png', mask)
        return mask
    if theme == 'test':
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_equi = np.array([80, 80, 84])
        upper_equi = np.array([120, 199, 255])
        mask = cv2.inRange(hsv, lower_equi, upper_equi)
        cv2.imwrite('fortuna_mask.png', mask)
        return mask


def prepare_img(img_src):
    upscaled = cv2.resize(img_src, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(upscaled, kernel, iterations=1)
    kernelled = cv2.erode(img, kernel, iterations=1)
    ret, imgtresh = cv2.threshold(create_mask("test", kernelled), 218, 255, cv2.THRESH_BINARY_INV)
    cv2.imwrite("theme_result.png", imgtresh)


img_source = "theme_source.png"
imgdata = cv2.imread(img_source)
prepare_img(imgdata)
