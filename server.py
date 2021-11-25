import socket
import pickle
import sys
import os
import struct
from ThreeWayHandshake import ThreeWayHandshake
from packet import Packet
from time import sleep
import time

localIP = socket.gethostbyname(socket.gethostname())
localPort = int(sys.argv[1])
bufferSize = 32780

ServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
ServerSocket.bind((localIP, localPort))

print(f"Server started at port {localPort}")
print("Listening to broadcast address for clients.")

listening = True
adrlist = []
# Listen for incoming datagrams
while listening:
    msg, adr = ServerSocket.recvfrom(32780)
    if adr not in adrlist:
        print(f"[!] Client {adr} found")
        adrlist.append(adr)
        listen_more = input("[?] Listen more? (y/n) ")
        if listen_more == "n":
            listening = False
            print("\n")

print(f"{len(adrlist)} clients found:")
for i in range(len(adrlist)):
    print(f"{i+1}. {adrlist[i]}")
print("\n")

ServerSocket.settimeout(1)
for i in range(len(adrlist)):
    obj = ThreeWayHandshake()
    connection = False
    while connection == False:
        try:
            print("Server Side: ", obj)
            ServerSocket.sendto(pickle.dumps(obj), adrlist[i])
            data = ServerSocket.recvfrom(bufferSize)[0]
            del obj
            obj = pickle.loads(data)
            del data
            print("Server side after response:", obj)
            obj.Connection()
            connection = obj.connected
            if obj.connected:
                ServerSocket.sendto(pickle.dumps(obj), adrlist[i])
                break
        except socket.error:
            print("Failed to make a connection")
            break

    if connection:
        print("Three-way done!!!\n")
        print("Start file transfer")
        # Go Back N
        path = open(sys.argv[2], "rb")
        N = 4
        FIN = False
        sn = 0
        sb = 0
        sm = N + 1
        inorder = False
        expected_seqnum = 0
        buffer = []
        finBuffer = {}
        EOT = False
        filesize = os.stat(sys.argv[2]).st_size
        sent = False
        start = time.time()
        while not sent:

            try:
                if(time.time() - start > 300): raise Exception("Timeout")
                # CHECK FOR ACK
                data, _ = ServerSocket.recvfrom(32780)
                p = Packet(byte_data=data)

                if p.get_flag() == b"\x10" and FIN:
                    print(
                        f"[Segment SEQ={p.get_seq_num()} ACK={p.get_ack_num()}] Receive ACK"
                    )
                    sent = True
                    print("Receive Fin ACK")
                    print("Sending ACK")
                    data, _ = ServerSocket.recvfrom(32780)
                    p = Packet(byte_data=data)
                    if p.get_flag() == b"\x10":
                        data, _ = ServerSocket.recvfrom(32780)
                        p = Packet(byte_data=data)
                        if p.get_flag() == b"\x10":
                            del finBuffer["fin"]
                            del finBuffer["ack"]
                            print(
                                f"[Segment SEQ={p.get_seq_num()} ACK={p.get_ack_num()}] Receive FIN ACK"
                            )
                            p = Packet(
                                flag=b"\x10",
                                seq_num=p.get_ack_num(),
                                ack_num=p.get_seq_num() + 1,
                            )
                            print(
                                f"[Segment SEQ={p.get_seq_num()} ACK={p.get_ack_num()}] Sending ACK"
                            )
                            ServerSocket.sendto(
                                p.get_packet_content(), adrlist[i])
                            print("[!] Connection Closing")
                            break
                        
                # IF ACK is In Order
                if p.get_ack_num() >= expected_seqnum and p.get_flag() == b"\x10" and not FIN:
                    print(f"[Segment SEQ={p.get_ack_num()}] Acked")
                    for j in range(expected_seqnum, p.get_ack_num() + 1):
                        buffer[j] = 0

                    expected_seqnum = p.get_ack_num() + 1
                    # Empty Buffer
                    # Slides Window
                    sb = p.get_ack_num()
                    sm = sb + N

                # Invalid Order
                elif p.get_flag() == b"\x10" and not EOT:
                    print("[!] Receive ACK: ", p.get_ack_num())
                    inorder = True

            except socket.error:
                # Send FIN
                if EOT and all(x == 0 for x in buffer) and not FIN:
                    print(f"[Segment SEQ={sn} ACK={sb}] Sending FIN, ACK")
                    p = Packet(flag=b"\x02", seq_num=sn, ack_num=sb)
                    finBuffer["fin"] = p
                    ServerSocket.sendto(p.get_packet_content(), adrlist[i])
                    p = Packet(flag=b"\x10", seq_num=sn, ack_num=sb)
                    finBuffer["ack"] = p
                    ServerSocket.sendto(p.get_packet_content(), adrlist[i])
                    FIN = True

                # Timeout Resend Buffer
                elif not all(x == 0 for x in buffer):
                    for j in range(len(buffer)):
                        if buffer[j] != 0:
                            ServerSocket.sendto(
                                buffer[j].get_packet_content(), adrlist[i])
                # Timeout FIN
                elif bool(finBuffer) and not sent:
                    print("[!] Timeout FIN Packet")
                    print("Resending FIN")
                    ServerSocket.sendto(finBuffer["fin"].get_packet_content(), adrlist[i])
                    print("Resending ACK")
                    ServerSocket.sendto(finBuffer["ack"].get_packet_content(), adrlist[i])
            except:
                print("Timeout client side error")
                sent = True
                break

            # ACK is out of order
            # Resend all packets in the window
            if inorder:
                print("[!!] Packet is out of order")
                # Resend packet
                for j in range(len(buffer)):
                    if buffer[j] != 0:
                        print("[!] Resending packet seq",
                              buffer[j].get_seq_num())
                        ServerSocket.sendto(
                            buffer[j].get_packet_content(), adrlist[i])
                inorder = False

            # sb <= sn <= sm
            if sn < sb + N and not EOT and all(x == 0 for x in buffer):
                Ntemp = N + sb - sn

                # Send packet in empty place
                while Ntemp > 0:
                    if filesize <= 0:
                        EOT = True
                        break
                    filedata = path.read(32768)

                    print(f"[Segment SEQ={sn}] Sent")
                    p = Packet(flag=b"\x00", seq_num=sn, data=filedata)
                    try:
                        buffer[sn] = p
                    except:
                        buffer.append(p)
                    ServerSocket.sendto(p.get_packet_content(), adrlist[i])
                    sn = sn + 1
                    # Final
                    filesize -= 32768
                    Ntemp -= 1
