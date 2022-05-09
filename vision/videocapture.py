import cv2
import threading

# bufferless VideoCapture
class VideoCapture:

    def __init__(self, name):
        self.cap = cv2.VideoCapture(name)
        self.width = self.cap.get(cv2. CAP_PROP_FRAME_WIDTH )
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT )
        self.t = threading.Thread(target=self._reader)
        self.t.daemon = True
        self.t.start()

    # grab frames as soon as they are available
    def _reader(self):
        while True:
            ret = self.cap.grab()
            if not ret:
                break

    # retrieve latest frame
    def read(self):
        ret, frame = self.cap.retrieve()
        return (ret, frame)
