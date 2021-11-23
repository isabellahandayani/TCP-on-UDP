import socket
import pickle
import sys
import os
import ThreeWayHandshake
from dummyPkt import Packet

localIP = socket.gethostbyname(socket.gethostname())
localPort = int(sys.argv[1])
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
    if listen_more == "n":
        listening = False
        print("\n")

print(f"{len(adrlist)} clients found:")
for i in range(len(adrlist)):
    print(f"{i+1}. {adrlist[i]}")
print("\n")

for i in range(len(conlist)):
    con = conlist[i]
    connection = False
    while connection == False:
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

    # Go Back N
    path = open(sys.argv[2], "rb")
    con.setblocking(0)
    N = 4
    FIN = False
    timeoutpd = 1
    sn = 0
    sb = 0
    sm = N + 1
    inorder = False
    expected_seqnum = 0
    buffer = []
    con.settimeout(timeoutpd)
    EOT = False
    filesize = os.stat(sys.argv[2]).st_size

    while not FIN:
        try:
            # CHECK FOR ACK
            data, _ = con.recvfrom(32766)
            p = Packet(byte_data=data)

            if p.get_flag() == b"\x02":
                print("[!] RECEIVE FIN FROM CLIENT")
                FIN = True
                break

            # IF ACK is In Order
            if p.get_ack_num() >= expected_seqnum and p.get_flag() == b"\x10":
                print("[!] Receive ACK: ", p.get_ack_num())
                for i in range(expected_seqnum, p.get_ack_num() + 1):
                    buffer[i] = 0

                expected_seqnum = p.get_ack_num()
                # Empty Buffer
                # Slides Window
                sb = p.get_ack_num() + 1
                sm = sb + N

            # Invalid Order
            elif p.get_flag() == b"\x10" and not EOT:
                print("[!] Receive ACK: ", p.get_ack_num())
                inorder = True

        except socket.error:
            # Send FIN
            if EOT and all(x == 0 for x in buffer):
                p = Packet(flag=b"\x02")
                con.sendall(p.get_packet_content())

            # Timeout Resend Buffer
            elif not all(x == 0 for x in buffer):
                for i in range(len(buffer)):
                    if buffer[i] != 0:
                        con.sendall(buffer[i].get_packet_content())

        # ACK is out of order
        # Resend all packets in the window
        if inorder:
            print("[!!] Packet is out of order")
            # Resend packet
            for i in range(len(buffer)):
                if buffer[i] != 0:
                    print("[!] Resending packet seq", buffer[i].get_seq_num())
                    con.sendall(buffer[i].get_packet_content())
            inorder = False

        if sn < sb + N and not EOT:  # sb <= sn <= sm
            Ntemp = N + sb - sn

            print(Ntemp)
            # Send packet in empty place
            while Ntemp > 0:
                filedata = path.read(32766)

                print("[!] Sending Packet Sn: ", sn)
                p = Packet(flag=b"\x00", seq_num=sn, data=filedata)
                try:
                    buffer[sn] = p
                except:
                    buffer.append(p)
                con.sendall(p.get_packet_content())
                sn = sn + 1
                # Final
                if filesize <= 32766:
                    EOT = True
                    break
                filesize -= 32766
                Ntemp -= 1
path.close()
