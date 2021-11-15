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
print("Listening to broadcast address for clients.")

listening = True
conlist = []
adrlist = []
# Listen for incoming datagrams
while listening:
	ServerSocket.listen(1)
	# Accept a connection and get a new socket object
	con, adr = ServerSocket.accept()
	print(f"[!] Client {adr} found")
	conlist.append(con)
	adrlist.append(adr)
	listen_more = input("[?] Listen more? (y/n) ")
	if(listen_more=='n'):
		listening = False
		print("\n")	

print(f"{len(adrlist)} clients found:")
for i in range(len(adrlist)):
	print(f"{i+1}. {adrlist[i]}")	
print("\n")	

for i in range(len(conlist)):
	con = conlist[i]	
	connection = False
	while connection == False :
		print("Waiting for connection")
		# Receive data on the connection
		data = con.recv(bufferSize)
		# Retrieve pickled data (ThreeWayHandshake object)
		obj = pickle.loads(data)
		# Delete data object
		del data
		print("Received.")
		# Call Connection from ThreeWayHandshake object
		obj.Connection()
		print("Server side:", obj)
		con.sendall(pickle.dumps(obj))
		connection = obj.IsConnected()
	print("Three-way done!!!\n")
	# Close socket object
	con.close()
