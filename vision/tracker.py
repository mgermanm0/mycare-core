import numpy as np
import cv2
import os
import time
from vision.spooler import Spooler
from vision.videocapture import VideoCapture
class AbstractTracker:
    def __init__(self) -> None:
        raise Exception("Abstract class cannot be instantiated")
    
    def track(self, frame, faces, device=0):
        pass

# Crea una zona de interés y si el detector detecta algo fuera de esa zona, intenta
# mover la cámara para centrar el objeto detectado (caras en este caso)
class RegionTracker(AbstractTracker):
    def __init__(self, controller, width, height) -> None:
        self.controller = controller
        self.spooler = Spooler()
        self.width = width
        self.height = height
        pass

    def track(self, frame, faces, device=0) -> None:
        centerScreenX = int(self.width/2)
        centerScreenY = int(self.height/2)
        offsetX = 100
        offsetY = 70
        X0_rect = centerScreenX-offsetX
        Y0_rect = centerScreenY-offsetY
        X1_rect = centerScreenX+offsetX
        Y1_rect = centerScreenY+offsetY
        text=""
        cv2.rectangle(frame, (X0_rect,Y0_rect), (X1_rect, Y1_rect), (0,100,0), 2)
        if faces is not None:
            text = "Sin caras"
            (x,y,w,h) = faces[0]
            centerX = int(x+w/2)
            centerY = int(y+h/2)
            if centerX >= centerScreenX-offsetX and centerX < centerScreenX+offsetX and centerY >= centerScreenY-offsetY and centerY < centerScreenY+offsetY:
                text="Dentro"
            else:
                #TODO test controller
                text="Fuera"
                tasks = []
                if centerY < centerScreenY-offsetY:
                    text+=" ^ "
                    #self.controller.up()
                    tasks.append((self.controller.up))
                elif centerX < centerScreenX-offsetX:
                    text+=" <- "
                    #self.controller.left()
                    tasks.append((self.controller.left))
                elif centerY >= centerScreenY+offsetY:
                    text+=" V "
                    #self.controller.down()
                    tasks.append((self.controller.down))
                elif centerX >= centerScreenX+offsetX:
                    text+=" -> "
                    #self.controller.right()
                    tasks.append((self.controller.right))
                if len(tasks) > 0:
                    self.spooler.addTasks(tasks)
            cv2.circle(frame, (centerX, centerY), 8, (255,0,0), -1)
        cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 2, cv2.LINE_AA)
            