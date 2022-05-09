from asyncio import tasks
import threading
import time
class Spooler:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.queue = []
        self.t = threading.Thread(target=self._spool)
        self.t.daemon = True
        self.t.start()
    
    def addTasks(self, tasks):
        self.lock.acquire()
        self.queue.extend(tasks)
        self.lock.release()
    
    def _spool(self):
        while True:
            self.lock.acquire()

            if len(self.queue) > 0:
                task = self.queue.pop(0)
                task()
            
            self.lock.release()