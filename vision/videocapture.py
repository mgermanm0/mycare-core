import cv2
import threading
import numpy as np
# bufferless VideoCapture
class VideoCapture:

    def __init__(self, name):
        self.cap = cv2.VideoCapture(name)
        self.width = 480
        self.height = 360
        print(self.width, self.height)
        self.t = threading.Thread(target=self._reader)
        self.t.daemon = True
        self.t.start()
        self.stop = False

    # grab frames as soon as they are available
    def _reader(self):
        while True:
            ret = self.cap.grab()
            if not ret or self.stop:
                return

    # retrieve latest frame
    def read(self):
        ret, frame = self.cap.retrieve()
        frame = cv2.resize(frame, (480,360))
        return (ret, frame)

    def release(self):
        self.stop = True
        self.t.join()
        self.cap.release()