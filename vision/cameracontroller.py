import subprocess
import time
UVCDYNCTRLEXEC="/usr/bin/uvcdynctrl"


class DeviceController():
    def __init__(self, device) -> None:
        self.deviceName = device
        self.panVal = 0
        self.tiltVal = 0
    
class CameraController(DeviceController):
    def __init__(self, device) -> None:
        DeviceController.__init__(self, device)
    
    def right(self, value="-100"):
        #print("Right")
        #if (value + self.panVal >= -4480):
        #self.panVal += value
        return subprocess.run([UVCDYNCTRLEXEC, "-d", self.deviceName, "-s" , "Pan (relative)", "--", value])
    
    def left(self, value="100"):
        #print("Left")
        #if (value + self.panVal <= 4480):
        #self.panVal += value
        return subprocess.run([UVCDYNCTRLEXEC, "-d", self.deviceName, "-s" , "Pan (relative)", "--", value])
        
    def up(self, value="-100"):
        #print("Up")
        #if (value + self.panVal >= -1920):
        #self.tiltVal += value
        return subprocess.run([UVCDYNCTRLEXEC, "-d", self.deviceName, "-s" , "Tilt (relative)", "--", value])
    
    def down(self, value="100"):
        #print("Down")
        #if (value + self.panVal <= 1920):
        #self.tiltVal += value
        return subprocess.run([UVCDYNCTRLEXEC, "-d", self.deviceName, "-s" , "Tilt (relative)", "--", value])
    
    def reset(self):
        subprocess.Popen([UVCDYNCTRLEXEC, "-d", self.deviceName, "-s" , "Pan Reset", "0"])
        time.sleep(3)
        subprocess.Popen([UVCDYNCTRLEXEC, "-d", self.deviceName, "-s" , "Tilt Reset", "0"])
        time.sleep(3)
        return 1
