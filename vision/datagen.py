import numpy as np
import cv2
import os
from constantes import DEBUG
class AbstractDatasetGenerator:
    def __init__(self) -> None:
        raise Exception("Abstract class cannot be instantiated")
    
    def generateDataset(self, name, device=0):
        pass
    
class FaceDatasetGenerator(AbstractDatasetGenerator):
    def __init__(self, detector=None, save_path="./") -> None:
        self.detector = detector
        self.save_path=save_path
        pass

    def generateDataset(self, name, cap) -> None:
        os.mkdir(self.save_path + name)
        image_cont = 0
        while(image_cont < 50):
            ret, frame = cap.read()
            faces = self.detector.detect(frame)
            if faces is not None:
                for (x,y,w,h) in faces:
                    face_img = frame[y:y+h, x:x+w]
                    cv2.imwrite(self.save_path + f'{name}' +os.sep+f'{name}_{image_cont}.png', face_img)
                    image_cont += 1
                    if DEBUG:
                        cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)