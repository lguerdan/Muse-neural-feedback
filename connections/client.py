import socket, time

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect(('localhost', 8089))
print "connected"

while 1:
	time.sleep(.1) 
	data = clientsocket.recv(512)
	print data
