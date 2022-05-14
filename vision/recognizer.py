from email.encoders import encode_noop
import encodings
from operator import sub
from unicodedata import name
import numpy as np
import face_recognition
import cv2
import pickle
import os
import numpy

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
    # https://projectgurukul.org/deep-learning-project-face-recognition-with-python-opencv/
    def train(self):
        for subdir, dirs, files in os.walk(rootdir + os.sep + "vision" + os.sep + "datasets" + os.sep):
            cont = 0
            totalCont = 0
            label = subdir.split(os.sep)[-1]
            if label in self.names:
                continue
            for file in files:
                #print os.path.join(subdir, file)
                filepath = subdir + os.sep + file
                #print (filepath)
                image = cv2.imread(filepath)
                rgbimg = image[:, :, ::-1]
                height, width, channels = rgbimg.shape
                #resized_img = cv2.resize(image, (0,0), fx=0.25, fy=0.25)
                encodigns = face_recognition.face_encodings(rgbimg)
                if len(encodigns) > 0:
                    encodign = encodigns[0]
                    self.names.append(label)
                    self.encodigns.append(encodign)
                    cont+=1
                totalCont+=1
            print("Para " , subdir, " se han encontrado " , totalCont, "caras de las cuales ", cont, "han sido usadas para el entrenamiento")
    
    def recognize(self, face):
        #resized_img = cv2.resize(face, (0,0), fx=0.25, fy=0.25)
        rgb = face[:, :, ::-1] # BGR 2 RGB
        #cv2.imshow("face", rgb)
        encoding = face_recognition.face_encodings(rgb)
        if len(encoding) == 0:
            return "Desconocido"
        matches = face_recognition.compare_faces(numpy.array(self.encodigns),
			encoding, 0.5)
        trueMatches = [i for (i,b) in enumerate(matches) if b]
        if len(trueMatches) == 0:
            return "Desconocido"
        
        cont = {}
        for i in trueMatches:
            nombre = self.names[i]
            cont[nombre] = cont.get(nombre, 0) + 1
        name_match = max(cont, key=cont.get)
        return name_match
        