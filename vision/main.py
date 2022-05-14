import threading
from sympy import root
from constantes import DEBUG
from vision.datagen import FaceDatasetGenerator
from vision.detector import HaarCascadeDetector
from vision.cameracontroller import CameraController
from vision.tracker import RegionTracker
from vision.videocapture import VideoCapture
from vision.recognizer import FaceRecognizer
import cv2
import os
rootdir = os.getcwd()

class AsistenteVision():
    def __init__(self, deviceName, deviceID, asistente) -> None:
        self.deviceName = deviceName
        self.deviceID = deviceID
        self.asistente = asistente
        self.entrena = False
        self.nombre = ""
        self.lockEntreno = threading.Lock()

    def mycare_vision_start(self):
        self.cap = VideoCapture(self.deviceID)
        self.cam = CameraController(self.deviceName)
        self.detector = HaarCascadeDetector()
        self.tracker = RegionTracker(self.cam, self.cap.width, self.cap.height)
        self.recognizer = FaceRecognizer()
        self.generator = FaceDatasetGenerator(detector=self.detector, save_path=rootdir + os.sep + "vision" + os.sep + "datasets" + os.sep)
        #generator = FaceDatasetGenerator(detector=detector, save_path="D:\\ProyectosPyCharm\\asistente\\vision\\datasets\\")
        #generator.generateDataset(name="manuelgm")
        self.__start()
        pass
    
    def setEntreno(self, name):
        self.lockEntreno.acquire()
        self.nombre = name
        self.entrena = True
        self.lockEntreno.release()

    def __start(self) -> None:
            cont = 0
            self.recognizer.train()
            self.cam.reset()
            while(True):
                self.lockEntreno.acquire()
                if not self.entrena:
                    self.lockEntreno.release()
                    ret, frame = self.cap.read()
                    faces = self.detector.detect(frame)
                    if faces is not None:
                        x,y,w,h = faces[0]
                        face_img = frame[y:y+h, x:x+w]
                        self.tracker.track(frame, faces)
                        user = self.recognizer.recognize(face_img)
                        if user != "Desconocido":
                            self.asistente.setUsername(user)
                        print(user)
                    if DEBUG:
                        cv2.imshow("cv", frame)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                else:
                    if self.nombre.lower() in self.recognizer.names:
                        self.asistente.talk("Vaya, parece que ya se quien eres. ¡No te reconocía " + self.nombre + "!")
                    else:
                        self.asistente.talk("Por favor, mira a la cámara.")
                        self.generator.generateDataset(self.nombre, self.cap)
                        self.asistente.talk("Gracias!")
                        self.recognizer.train()
                    self.entrena = False
                    self.name = ""
                    self.lockEntreno.release()
            self.cap.release()
            cv2.destroyAllWindows()