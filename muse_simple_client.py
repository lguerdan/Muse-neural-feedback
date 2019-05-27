from queue import Queue
from threading import Thread
from listening_server import MuseServer
import time, websocket, json
from functools import partial
import socket

# A sample listening client, could be anything on the network you want to talk to 

def muse_listener_producer(out_q):
   server = MuseServer(out_q)
   server.start()
   while 1:
      time.sleep(1)

def consumer(in_q):

   serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   serversocket.bind(('localhost', 8089))
   serversocket.listen(5) # become a server socket, maximum 5 connections

   while True:
      connection, address = serversocket.accept()
      print "connected"
      while True:

         data = in_q.get()
         packet = json.dumps(data, ensure_ascii=False)
         print "details:" + packet

         connection.send(json.dumps(data))


# Set up messaging que for passing data from OSM server thread to data processing thread
q = Queue()

#Thread for lissening to new data packets
t2 = Thread(target=muse_listener_producer, args=(q,))
t2.daemon = True

#Thread for processing those data packets
t1 = Thread(target=consumer, args=(q,))
t1.daemon = True

t2.start()
t1.start()

while True:
   time.sleep(1)