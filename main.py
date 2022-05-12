from pln.prueba import AsistenteVoz
from vision.main import mycare_vision_start
import threading

def main():
    print("On!")
    asistente = AsistenteVoz()
    #vision_thread = threading.Thread(name="vision-thread", target=mycare_vision_start, args=(asistente, ))
    #vision_thread.start()
    #asistente.setUsername("Manuel")
    asistente.mycare_pln_start()
    pass
if __name__ == "__main__":
    main()