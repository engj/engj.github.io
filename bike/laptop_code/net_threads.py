import pickle
import socket
import threading
from time import sleep
import serial, io


class PushThread ( threading.Thread ):

   def __init__(self, queue, ip, port):
      threading.Thread.__init__(self)
      self.queue = queue
      self.ip = ip
      self.port = port
      self._stop = threading.Event()

   def run ( self ):
      client = socket.socket ( socket.AF_INET, socket.SOCK_DGRAM )

      while True:
         tosend = self.queue.get()
         client.sendto(tosend, (self.ip, self.port))
      
      client.close()

   def stop(self):
       self._stop.set()



class PullThread(threading.Thread):

    def __init__(self, queue, port):
        threading.Thread.__init__(self)
        self.queue = queue
        self.port = port
        self._stop = threading.Event()

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.bind(('', self.port))
 
        while True:
            self.queue.put(server.recvfrom(1024)[0])

        server.close()

    def stop(self):
        self._stop.set()


class ArdReadThread(threading.Thread):
    def __init__(self, queue, device, speed):
        threading.Thread.__init__(self)
        self.device = device
        self.speed = speed
        self.queue = queue
        self._stop = threading.Event()

    def run(self):
        wser = serial.Serial(self.device, self.speed)
        while True:
            line = wser.readline()
            self.queue.put(line)

    def stop(self):
        self._stop.set()


class ArdWriteThread(threading.Thread):
    def __init__(self, queue, device, speed):
        threading.Thread.__init__(self)
        self.device = device
        self.speed = speed
        self.queue = queue
        self._stop = threading.Event()

    def run(self):
        rser = serial.Serial(self.device, self.speed)
        while True:
            msg = self.queue.get()
            rser.write(msg)            

    def stop(self):
        self._stop.set()
