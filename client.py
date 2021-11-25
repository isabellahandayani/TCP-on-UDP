import socket
import pickle
import sys
import struct
from ThreeWayHandshake import ThreeWayHandshake
from packet import Packet
from time import sleep

clientAddressPort = (socket.gethostbyname(socket.gethostname()), int(sys.argv[1]))
serverAddressPort = (socket.gethostbyname(socket.gethostname()), 3000)

path = open(sys.argv[2], "w")

bufferSize = 4096

ClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Create new object from ThreeWayHandshake class
obj = ThreeWayHandshake()

# Connect to server
ClientSocket.sendto(b"", serverAddressPort)
# Call Connection from ThreeWayHandshake object
obj.Connection()

while obj.connected == False:
    print("Client side:", obj)
    ClientSocket.sendto(pickle.dumps(obj), serverAddressPort)
    if obj.connected == True:
        break
    del obj
    data = ClientSocket.recvfrom(bufferSize)[0]
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

while True:
    data, address = ClientSocket.recvfrom(32780)
    p = Packet(byte_data=data)

    # TODO checksum V
    if p.get_seq_num() == rn and p.get_flag() == b"\x00" and p.get_checksum() == struct.pack("H", p.generate_checksum()):
        print(f"[Segment SEQ={p.get_seq_num()}] Received, ACK sent" )
        path.write(p.get_message().decode())
        rn = rn + 1
        ack_num = p.get_seq_num()
    else:
        print(f"[Segment SEQ={p.get_seq_num()}] Received, ACK sent" )


    if p.get_flag() == b"\x00":
        ack = Packet(flag=b"\x10", ack_num=ack_num)
        ClientSocket.sendto(ack.get_packet_content(), address)

    if p.get_flag() == b"\x02":
        print("[!] Receive FIN")
        p = Packet(flag=b"\x10", seq_num=rn, ack_num=ack_num)
        print("[!] Sending ACK")
        ClientSocket.sendto(p.get_packet_content(), address)
        p = Packet(flag=b"\x02", seq_num=rn, ack_num=ack_num)
        ClientSocket.sendto(p.get_packet_content(), address)
        print("[!] Sending FIN")
        break


path.close()
