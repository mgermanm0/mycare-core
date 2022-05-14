import numpy as np
import cv2

class AbstractDetector:
    def __init__(self) -> None:
        raise Exception("Abstract class cannot be instantiated")
    
    def detect(self, frame):
        pass

class HaarCascadeDetector(AbstractDetector):
    def __init__(self, cascadePath=cv2.data.haarcascades + 'haarcascade_frontalface_default.xml') -> None:
        self.haarDetectors = []
        classifier = cv2.CascadeClassifier()
        print(cascadePath)
        classifier.load(cascadePath)
        self.haarDetectors.append(classifier)
        pass
    
    def detect(self, frame):
        byn = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        byn = cv2.equalizeHist(byn)
        for haardetector in self.haarDetectors:
            faces = haardetector.detectMultiScale(byn, scaleFactor=1.1, minNeighbors=5, minSize=(35,35), flags=cv2.CASCADE_SCALE_IMAGE)
            if len(faces) > 0:
                return faces
        return None