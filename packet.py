import struct
import math


class Packet:
    """
    Sequence number = 4 bytes
    Ack number = 4 bytes
    Flags = 1 byte
    Checksum = 2 bytes
    Data = Max 32768 bytes
    """

    def __init__(self, seq_num=0, ack_num=0, flag=b"", data=b"", byte_data=None):
        if byte_data is not None:
            self.seq_num = struct.pack("I", int.from_bytes(byte_data[0:4], "little"))
            self.ack_num = struct.pack("I", int.from_bytes(byte_data[4:8], "little"))
            self.flag = struct.pack("B", byte_data[8])
            self.checksum = struct.pack("H", int.from_bytes(byte_data[10:12], "little"))
            self.data = struct.pack(f"{len(byte_data[12:])}s", byte_data[12:])
            self.data_length = len(byte_data[12:])
            return

        try:
            if len(data) > 32768:
                print("SINI")
                raise Exception("Data too long")
        except:
            pass
        self.seq_num = struct.pack("I", seq_num)
        self.ack_num = struct.pack("I", ack_num)
        self.flag = struct.pack("s", flag)
        self.data = struct.pack(f"{len(data)}s", data)
        self.data_length = struct.pack("2s", len(data).to_bytes(2, "little"))
        self.checksum = struct.pack("H", self.generate_checksum())

        self.packet_content = (
            self.seq_num
            + self.ack_num
            + self.flag
            + struct.pack("s", b"")
            + self.checksum
            + self.data
        )

    def get_seq_num(self):
        return struct.unpack("I", self.seq_num)[0]

    def get_ack_num(self):
        return struct.unpack("I", self.ack_num)[0]

    def get_flag(self):
        return struct.unpack("s", self.flag)[0]

    def get_message(self):
        return struct.unpack(f"{self.data_length}s", self.data)[0]

    def get_checksum(self):
        return self.checksum

    def get_packet_content(self):
        return self.packet_content

    def get_message(self):
        return struct.unpack(f"{self.get_data_length()}s", self.data)[0]

    def get_data_length(self):
        return self.data_length

    def print_packet_info(self):
        print(f"seq_num = {self.seq_num} ({self.get_seq_num()})")
        print(f"ack_num = {self.ack_num} ({self.get_ack_num()})")
        print(f"flag = {self.flag} ({self.get_flag()})")
        print(f"checksum = {self.checksum}")

    def generate_checksum(self):
        checksum = 0xFFFF & 0
        content = bytearray(self.seq_num + self.ack_num + self.flag + self.data)
        chunks = [content[i : i + 2] for i in range(0, len(content), 2)]
        for chunk in chunks:
            if len(chunk) == 1:
                # padding byte
                chunk += struct.pack("x")
            checksum = 0xFFFF & (checksum + struct.unpack(">H", chunk)[0])
        return ~checksum & 0xFFFF

