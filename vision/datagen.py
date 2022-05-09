import numpy as np
import cv2
import os

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

    def generateDataset(self, name, device=0) -> None:
        os.mkdir(self.save_path + name)
        cap = cv2.VideoCapture(device)
        image_cont = 0
        while(image_cont < 50):
            ret, frame = cap.read()
            faces = self.detector.detect(frame)
            if faces is not None:
                for (x,y,w,h) in faces:
                    face_img = frame[y:y+h, x:x+w]
                    cv2.imwrite(self.save_path + f'{name}\\{name}_{image_cont}.png', face_img)
                    image_cont += 1
                    cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)
            cv2.imshow("cv", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()