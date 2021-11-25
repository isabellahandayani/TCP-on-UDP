class ThreeWayHandshake:
    def __init__(self, twh=None):

        self.status = None
        self.connected = False

    def Connection(self):
        if self.status == None:
            print("Three-way handshake", "Status: SYN", sep="\n")
            self.status = "SYN"
        elif self.status == "SYN":
            print("SYN received", "Status: ACK-SYN", sep="\n")
            self.status = "ACK-SYN"
        elif self.status == "ACK-SYN":
            print("ACK-SYN received", "Status: ACK", sep="\n")
            self.status = "ACK"
        elif self.status == "ACK":
            self.connected = True
            print("Connected.", "Ready to transfer data.", sep="\n")

    def IsConnected(self):
        return self.connected

    def Reset(self):
        self.status = None
        self.connected = False

    def __str__(self):
        return f"Status: {self.status}, connection established: {self.connected}."
