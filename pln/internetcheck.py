from sqlite3 import connect
import urllib.request

class InternetCheck():
    def __init__(self, executeIfDown, executeIfUp) -> None:
        self.executeIfDown = executeIfDown
        self.executeIfUp = executeIfUp
        self.isDown = False
        
    def checkInternet(self):
        print("Comprobando conexión...")
        connected = True
        try:
            urllib.request.urlopen("https://www.google.es")
        except:        
            connected = False
        
        if not connected and not self.isDown:
            self.isDown = True
            if self.executeIfDown is not None:
                self.executeIfDown()
        
        if connected and self.isDown:
            self.isDown = False
            if self.executeIfUp is not None:
                self.executeIfUp()
        
        