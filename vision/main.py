from vision.datagen import FaceDatasetGenerator
from vision.detector import HaarCascadeDetector
from vision.cameracontroller import CameraController
from vision.tracker import RegionTracker
from vision.videocapture import VideoCapture
#from recognizer import FaceRecognizer
import cv2

def mycare_vision_start(asistente):

    #generator = FaceDatasetGenerator(detector=detector, save_path="D:\\ProyectosPyCharm\\asistente\\vision\\datasets\\")
    #generator.generateDataset(name="manuelgm")
    start(asistente)
    pass

def start(asistente, device=0) -> None:
        cont = 0
        cam = CameraController("/dev/video0")
        cam.reset()
        detector = HaarCascadeDetector()
        cap = VideoCapture(device)
        tracker = RegionTracker(cam, cap.width, cap.height)
        #recognizer = FaceRecognizer()
        while(True):
            ret, frame = cap.read()
            faces = detector.detect(frame)
            if faces is not None:
                tracker.track(frame, faces, device=0)
                asistente.setUsername("Manuel")
                #recognizer.recognize(faces[0])
            cv2.imshow("cv", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
    
if __name__ == "__main__":
    mycare_vision_start()