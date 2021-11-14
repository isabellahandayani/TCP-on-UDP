import socket
import pickle
from ThreeWayHandshake import ThreeWayHandshake
from time import sleep

serverAddressPort   = ("127.0.0.1", 3000)
bufferSize = 4096

ClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

# Create new object from ThreeWayHandshake class
obj = ThreeWayHandshake()

# Connect to server
ClientSocket.connect(serverAddressPort)
# Call Connection from ThreeWayHandshake object
obj.Connection()

while obj.connected == False:
	print("Client side:", obj)
	ClientSocket.sendall(pickle.dumps(obj))
	if obj.connected == True:
		break
	del obj
	data = ClientSocket.recv(bufferSize)
	sleep(1)
	obj = pickle.loads(data)
	del data
	print("Client side after response:", obj)
	obj.Connection()
	sleep(3)

print("Done.") if obj.connected == True else print("Not done")
