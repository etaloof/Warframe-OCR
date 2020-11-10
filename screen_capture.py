import time

import cv2
import mss
import numpy as np


class Screenshots:
    def __init__(self, sct, monitor=1):
        self.sct = sct
        self.monitor = monitor

    def take_screenshot(self):
        return next(iter(self))

    def __iter__(self):
        while True:
            monitor = self.sct.monitors[self.monitor]
            yield np.array(self.sct.grab(monitor))


def show_screenshots_with_fps():
    with mss.mss() as sct:
        while True:
            start = time.time()
            img = np.array(sct.grab(sct.monitors[1]))
            end = time.time()
            frametime = (end - start)
            fps = 1 / frametime
            fps = np.round(fps, 2)

            width = int(img.shape[1] * 0.3)
            height = int(img.shape[0] * 0.3)
            dim = (width, height)
            display = cv2.resize(img, dim)
            display = cv2.putText(display, str(fps), (0, height - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            cv2.imshow('screenshot', display)
            cv2.waitKey(1)


def show_screenshots_without_fps():
    with mss.mss() as sct:
        for img in Screenshots(sct):
            width = int(img.shape[1] * 0.3)
            height = int(img.shape[0] * 0.3)
            dim = (width, height)
            display = cv2.resize(img, dim)
            cv2.imshow('screenshot', display)
            cv2.waitKey(1000)


if __name__ == '__main__':
    show_screenshots_without_fps()
