from unicodedata import name
import numpy as np
import face_recognition
import cv2
import pickle
import os

rootdir = os.getcwd()


class Recognizer:
    def __init__(self) -> None:
        raise Exception("Abstract classes cannot be instantiated")
    
    def train(dataset):
        pass

    def recognize(frame):
        pass

class FaceRecognizer(Recognizer):
    def __init__(self) -> None:
        self.encodigns = []
        self.names = []
        self.id = 0
        super().__init__()
    # https://projectgurukul.org/deep-learning-project-face-recognition-with-python-opencv/
    def train(self):
        for subdir, dirs, files in os.walk(rootdir+os.sep + "datasets"):
            for file in files:
                #print os.path.join(subdir, file)
                filepath = subdir + os.sep + file
                print (filepath)
                image = cv2.imread(file)
                rgbimg = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                #resized_img = cv2.resize(image, (0,0), fx=0.25, fy=0.25)
                encodign = face_recognition.face_encodings(rgbimg)[0]
                self.names.append(subdir)
                self.encodigns.append(encodign)
                self.id+=1
    
    def recognize(self, face):
        #resized_img = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)
        rgbimg = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        encoding = face_recognition.face_encodings(rgbimg)
        matches = face_recognition.compare_faces(self.encodigns,
			encoding)
        trueMatches = [i for (i,b) in enumerate(matches) if b]
        if len(trueMatches) == 0:
            return "Desconocido"
        
        cont = {}
        for i in trueMatches:
            nombre = self.names[i]
            cont[nombre] = cont.get(nombre, 0) + 1
        name_match = max(cont, key=cont.get)
        return name_match
        
