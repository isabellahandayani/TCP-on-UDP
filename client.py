import socket
import pickle
import sys
import struct
import ThreeWayHandshake
import time
from packet import Packet

clientAddressPort = (socket.gethostbyname(
    socket.gethostname()), int(sys.argv[1]))
serverAddressPort = (socket.gethostbyname(socket.gethostname()), 3000)

path = open(sys.argv[2], "wb")

bufferSize = 32780

ClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Create new object from ThreeWayHandshake class

# Connect to server
ClientSocket.sendto(b"", serverAddressPort)
# Call Connection from ThreeWayHandshake object
start = time.time()
connection = False
print("Waiting for connection")
while connection == False:
    try:
        if(time.time() - start > 300): raise Exception("Timeout")
        # Receive data on the connection
        data = ClientSocket.recvfrom(bufferSize)[0]
        # Retrieve pickled data (ThreeWayHandshake object)
        obj = pickle.loads(data)
        # Delete data object
        del data
        print("Received.")
        # Call Connection from ThreeWayHandshake object
        obj.Connection()
        print("Client side:", obj)
        ClientSocket.sendto(pickle.dumps(obj), serverAddressPort)
        connection = obj.IsConnected()
    except:
        print("Failed to make connection")
        break

ClientSocket.settimeout(5)
if connection:
    # GO BACK N
    N = 4
    ack_num = 0
    rn = 0

    while True:
        data, address = ClientSocket.recvfrom(32780)
        p = Packet(byte_data=data)

        # TODO checksum V
        if (
            p.get_seq_num() == rn
            and p.get_flag() == b"\x00"
            and p.get_checksum() == struct.pack("H", p.generate_checksum())
        ):
            print(f"[Segment SEQ={p.get_seq_num()}] Received, ACK sent")
            path.write(p.get_message())
            rn = rn + 1
            ack_num = p.get_seq_num()
        elif p.get_flag() == b"\x00":
            print(f"[Segment SEQ={p.get_seq_num()}] Received, ACK sent")

        if p.get_flag() == b"\x00":
            ack = Packet(flag=b"\x10", ack_num=ack_num)
            ClientSocket.sendto(ack.get_packet_content(), address)
        if p.get_flag() == b"\x02":
            data, address = ClientSocket.recvfrom(32780)
            p = Packet(byte_data=data)
            if p.get_flag() == b"\x10":
                print(
                    f"[Segment SEQ={p.get_seq_num()} ACK={p.get_ack_num()}] Receive FIN, ACK"
                )
                ack = Packet(
                    flag=b"\x10", seq_num=p.get_ack_num(), ack_num=p.get_seq_num() + 1
                )
                print(
                    f"[Segment SEQ={ack.get_seq_num()} ACK={ack.get_ack_num()}] Sending ACK"
                )
                ClientSocket.sendto(ack.get_packet_content(), address)
                fin = Packet(
                    flag=b"\x02", seq_num=p.get_ack_num(), ack_num=p.get_seq_num() + 1
                )
                ClientSocket.sendto(fin.get_packet_content(), address)
                ack = Packet(
                    flag=b"\x10", seq_num=p.get_ack_num(), ack_num=p.get_seq_num() + 1
                )
                ClientSocket.sendto(ack.get_packet_content(), address)
                print(
                    f"[Segment SEQ={ack.get_seq_num()} ACK={ack.get_ack_num()}] Sending FIN, ACK"
                )
                break


path.close()
