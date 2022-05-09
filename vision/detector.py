import numpy as np
import cv2

class AbstractDetector:
    def __init__(self) -> None:
        raise Exception("Abstract class cannot be instantiated")
    
    def detect(self, frame):
        pass

class HaarCascadeDetector(AbstractDetector):
    def __init__(self, cascadesPath=[cv2.data.haarcascades + 'haarcascade_frontalface_default.xml', cv2.data.haarcascades + 'haarcascade_profileface.xml']) -> None:
        self.haarDetectors = []
        for cascade in cascadesPath:
            classifier = cv2.CascadeClassifier()
            print(cascade)
            classifier.load(cascade)
            self.haarDetectors.append(classifier)
        pass
    
    def detect(self, frame):
        byn = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        byn = cv2.equalizeHist(byn)
        for haardetector in self.haarDetectors:
            faces = haardetector.detectMultiScale(byn, scaleFactor=1.1, minNeighbors=5, minSize=(30,30), flags=cv2.CASCADE_SCALE_IMAGE)
            if len(faces) > 0:
                return faces
        return None