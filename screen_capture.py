import itertools
import sys
import time
from contextlib import contextmanager
from multiprocessing.dummy import Process, Queue
from queue import Full as QueueFullException

import cv2
import mss
import numpy as np
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QWidget, QApplication
from tesserocr import PSM, OEM

from ocr_local import spell_correction_ocr, RustyOcrCheck, TesserocrPool


def do_ocr(pool, image_input):
    spell_correction_ocr(None, None, set_selected=1)
    begin = time.time()

    if image_input.shape[:2] == (900, 1600):
        image_input = cv2.resize(image_input, (1920, 1080))
    ocr = RustyOcrCheck(pool, image_input)
    ocr_data = ocr.ocr_loop()

    end = time.time()
    delta = end - begin
    print(f'ocr took {delta}s')

    return ocr_data


class Screenshots:
    def __init__(self, sct, monitor=1):
        self.sct = sct
        self.monitor = monitor

    def take_screenshot(self):
        monitor = self.sct.monitors[self.monitor]
        return np.array(self.sct.grab(monitor))

    def __iter__(self):
        while True:
            yield next(self)

    def __next__(self):
        return self.take_screenshot()


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


class Widget(QWidget):

    def __init__(self, q):
        super().__init__()
        self.q = q

        self.setGeometry(1700, 300, 400, 350)
        self.setWindowTitle('Current relic detection state')
        self.show()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(500)

    def paintEvent(self, e):
        pad = 10
        width = 60
        height = 60
        text = "Each square shows where a relic is expected on the screen. " \
               "Red squares indicate that the relic at this position could not be detected, " \
               "green squares indicate that it could be detected (but the result could still be wrong)."

        with self.begin_draw() as qp:
            result = self.q.get()
            print(result)

            max_x = 0
            max_y = 0

            for i, result in enumerate(result):
                is_detection_error = result is None or any('ocrerror' in str(s).lower() for s in result)
                if is_detection_error:
                    color = QColor('red')
                else:
                    color = QColor('green')

                x = i % 5
                y = i // 5
                x = pad + (width + pad) * x
                y = pad + (height + pad) * y

                max_x = max(max_x, x)
                max_y = max(max_y, y)

                qp.setBrush(color)
                qp.drawRect(x, y, width, height)
                if not is_detection_error:
                    qp.drawText(x, y, width, height, Qt.AlignCenter | Qt.TextWordWrap, str(result))

            qp.drawText(pad, pad + max_y + height, max_x + width, height, Qt.AlignLeft | Qt.TextWordWrap, text)

    @contextmanager
    def begin_draw(self) -> QPainter:
        qp = QPainter()
        qp.begin(self)
        try:
            yield qp
        finally:
            qp.end()


def main(q=None):
    """
    Try to detect relics on the screen and show if they can be detected in a window.

    For some weird reason, Qt and tesseract cannot run in the same thread.
    Doing so leads to a crash and I'm unable to figure out the cause.
    We workaround this by creating a thread for Qt and putting all ocr result into a queue.
    :param q: A queue for communication with the Qt thread
    """
    if q is not None:
        app = QApplication(sys.argv)
        widget = Widget(q)
        sys.exit(app.exec_())

    q = Queue(1)
    p = Process(target=main, args=(q,))
    p.start()

    tessdata_dir = 'tessdata/'
    with TesserocrPool(tessdata_dir, 'Roboto', psm=PSM.SINGLE_BLOCK, oem=OEM.LSTM_ONLY) as pool, mss.mss() as sct:
        s = Screenshots(sct)
        while p.is_alive():
            begin = time.time()
            image_input = next(s)
            end = time.time()
            delta = end - begin
            print(f'screenshot took {delta}s')

            try:
                ocr_data = do_ocr(pool, image_input)
            except:
                ocr_data = None

            if ocr_data is None:
                ocr_data = itertools.repeat(('ocrerror',) * 4, 20)

            try:
                q.put(tuple(ocr_data), block=True, timeout=0.5)
            except QueueFullException:
                if not p.is_alive():
                    break
            except ValueError as e:
                pass
            except AssertionError as e:
                pass

    p.join()


if __name__ == '__main__':
    main()
