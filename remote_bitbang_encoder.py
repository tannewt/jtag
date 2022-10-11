from typing import Protocol
from low_level_jtag import LowLevelJTAG

from abc import abstractmethod

class RemoteBitbangEncoder(LowLevelJTAG):
    @abstractmethod
    def write_character(self, c: int):
        ...

    @abstractmethod
    def read_character(self) -> int:
        ...

    def blink_on(self):
        self.write_character(66)

    def blink_off(self):
        self.write_character(98)

    def read_tdo(self):
        self.write_character(82)
        return self.read_character() == 49

    def quit(self):
        self.write_character(81)

    def write(self, *, tck, tms, tdi):
        val = 48 # character 0
        if tck:
            val += 4
        if tms:
            val += 2
        if tdi:
            val += 1
        self.write_character(val)

    def reset(self, *, trst, srst):
        val = 114 # ASCII character r
        if trst:
            val += 2
        if srst:
            val += 1
        self.write_character(val)
