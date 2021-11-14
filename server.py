import socket
import pickle
import ThreeWayHandshake

localIP = "127.0.0.1"
localPort = 3000
bufferSize = 4096

ServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

# Bind to address and ip
ServerSocket.bind((localIP, localPort))

print(f"Server started at port {localPort}")

# Listen for incoming datagrams
ServerSocket.listen(1)
# Accept a connection and get a new socket object
con = (ServerSocket.accept()[0])
connection = False
while connection == False:
	print("Wating for connection")
	# Receive data on the connection
	data = con.recv(bufferSize)
	# Retrieve pickled data (ThreeWayHandshake object)
	obj = pickle.loads(data)
	# Delete data object
	del data
	print("Recieved.")
	# Call Connection from ThreeWayHandshake object
	obj.Connection()
	print("Server side:", obj)
	con.sendall(pickle.dumps(obj))
	connection = obj.IsConnected()
print("Three-way done!!!")
# Close socket object
con.close()
