from pln.prueba import AsistenteVoz
from vision.main import AsistenteVision
import threading
import time
def main():
    print("On!")
    asistentevoz = AsistenteVoz()
    asistentevision = AsistenteVision("video0", 0, asistentevoz)
    """
    vision_thread = threading.Thread(name="vision-thread", target=asistentevision.mycare_vision_start)
    vision_thread.start()
    """
    voz_thread = threading.Thread(name="voz-thread", target=asistentevoz.mycare_pln_start)
    asistentevoz.asistentevision = asistentevision
    voz_thread.start()
    asistentevision.mycare_vision_start()
    pass
if __name__ == "__main__":
    main()