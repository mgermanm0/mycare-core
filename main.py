from pln.prueba import mycare_pln_start
from vision.main import mycare_vision_start
import threading

def main():
    print("On!")
    """
    vision_thread = threading.Thread(name="vision-thread", target=mycare_vision_start)
    vision_thread.start()
    vision_thread.join()
    """
    mycare_pln_start()
    
    #mycare_vision_start()
    pass
    
if __name__ == "__main__":
    main()