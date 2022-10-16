from remote_bitbang_encoder import RemoteBitbangEncoder
import time

class RemoteSocket(RemoteBitbangEncoder):
    def __init__(self, socket):
        self.socket = socket
        self.buf = bytearray(1)

    def write_character(self, c: int):
        self.buf[0] = c
        sent = self.socket.send(self.buf)

    def read_character(self) -> int:
        self.socket.recv_into(self.buf)
        return self.buf[0]
