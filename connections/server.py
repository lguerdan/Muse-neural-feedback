import socket, time, random,json

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('localhost', 8089))
serversocket.listen(5) # become a server socket, maximum 5 connections

while True:
	connection, address = serversocket.accept()
	print "connected"
	while True:
		time.sleep(.1)
		ar, bc, tr = random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)
		packet = {"alpha-relaxation": ar, "beta-concentration": bc, "theta-relaxation":tr }
		connection.send(json.dumps(packet))

