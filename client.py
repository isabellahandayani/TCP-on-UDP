import socket
import pickle
import sys
from ThreeWayHandshake import ThreeWayHandshake
from dummyPkt import Packet
from time import sleep

clientAddressPort = (socket.gethostbyname(socket.gethostname()), int(sys.argv[1]))
serverAddressPort = (socket.gethostbyname(socket.gethostname()), 3000)

path = open(sys.argv[2], "w")

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

print("Done.") if obj.connected == True else print("Not done")

# GO BACK N
N = 4
ack_num = 0
rn = 0

# p = Packet(flag=b"\x02", seq_num=rn, ack_num=ack_num)
# s.send(p.get_packet_content())


while True:
    data, address = ClientSocket.recvfrom(32766)
    p = Packet(byte_data=data)

    # TODO checksum V
    if p.get_seq_num() == rn and p.get_flag() == b"\x00":
        print("[!] Receive Packet SEQ ", p.get_seq_num())
        print("[!] Write to file")
        path.write(p.get_message().decode())
        rn = rn + 1
        ack_num = p.get_seq_num()

    if p.get_flag() == b"\x00":
        print("[!} Send ACK: ", ack_num)
        ack = Packet(flag=b"\x10", ack_num=ack_num)
        ClientSocket.send(ack.get_packet_content())

    if p.get_flag() == b"\x02":
        print("[!] Receive FIN")
        p = Packet(flag=b"\x10", seq_num=rn, ack_num=ack_num)
        print("[!] Sending ACK")
        ClientSocket.send(p.get_packet_content())
        p = Packet(flag=b"\x02", seq_num=rn, ack_num=ack_num)
        ClientSocket.send(p.get_packet_content())
        print("[!] Sending FIN")
        break


path.close()
