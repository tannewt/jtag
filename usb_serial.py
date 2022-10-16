from remote_bitbang_encoder import RemoteBitbangEncoder
import serial as pyserial


class USBSerialEncoder(RemoteBitbangEncoder):
    def __init__(self, device):
        self.serial = pyserial.Serial(device)
        self.buf = bytearray(1)

    def write_character(self, c: int):
        self.buf[0] = c
        self.serial.write(self.buf)

    def read_character(self) -> int:
        self.serial.readinto(self.buf)
        return self.buf[0]

    def quit(self):
        super().quit()
        self.serial.close()
