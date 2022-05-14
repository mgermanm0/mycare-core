from pln.prueba import AsistenteVoz
from vision.main import AsistenteVision
import threading
import time
def main():
    print("On!")
    asistentevoz = AsistenteVoz()
    asistentevision = AsistenteVision("video2", 2, asistentevoz)
    vision_thread = threading.Thread(name="vision-thread", target=asistentevision.mycare_vision_start)
    vision_thread.start()
    asistentevoz.asistentevision = asistentevision
    asistentevoz.mycare_pln_start()
    pass
if __name__ == "__main__":
    main()