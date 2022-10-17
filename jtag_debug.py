from typing import Protocol
from low_level_jtag import LowLevelJTAG

from abc import abstractmethod

STATE_MACHINE = {
    "Test-Logic-Reset": {True: "Test-Logic-Reset", False: "Run-Test/Idle"},
    "Run-Test/Idle":    {True: "Select-DR-Scan", False: "Run-Test/Idle"},

    "Select-DR-Scan":   {True: "Select-IR-Scan", False: "Capture-DR"},
    "Capture-DR":       {True: "Exit1-DR", False: "Shift-DR"},
    "Shift-DR":         {True: "Exit1-DR", False: "Shift-DR"},
    "Exit1-DR":         {True: "Update-DR", False: "Pause-DR"},
    "Pause-DR":         {True: "Exit2-DR", False: "Pause-DR"},
    "Exit2-DR":         {True: "Update-DR", False: "Shift-DR"},
    "Update-DR":        {True: "Select-DR-Scan", False: "Run-Test/Idle"},

    "Select-IR-Scan":   {True: "Test-Logic-Reset", False: "Capture-IR"},
    "Capture-IR":       {True: "Exit1-IR", False: "Shift-IR"},
    "Shift-IR":         {True: "Exit1-IR", False: "Shift-IR"},
    "Exit1-IR":         {True: "Update-IR", False: "Pause-IR"},
    "Pause-IR":         {True: "Exit2-IR", False: "Pause-IR"},
    "Exit2-IR":         {True: "Update-IR", False: "Shift-IR"},
    "Update-IR":        {True: "Select-DR-Scan", False: "Run-Test/Idle"},
}

class Debug(LowLevelJTAG):
    def __init__(self, ll):
        self.ll = ll
        self.current_state = "Test-Logic-Reset"
        self.last_clock = None

    def blink_on(self):
        print("Blink on")
        self.ll.blink_on()

    def blink_off(self):
        print("Blink off")
        self.ll.blink_off()

    def read_tdo(self):
        v = self.ll.read_tdo()
        print("Read:", v)
        return v

    def quit(self):
        print("Quit")
        self.ll.quit()

    def write(self, *, tck, tms, tdi):
        print("write tck:", tck, "tms:", tms, "tdi:", tdi)
        if self.last_clock is not None:
            if not self.last_clock and tck:
                next_state = STATE_MACHINE[self.current_state][tms]
                if next_state != self.current_state:
                    print(next_state)
                self.current_state = next_state
            if self.last_clock == tck:
                raise RuntimeError("Clock must change between each write.")
        self.last_clock = tck
        self.ll.write(tck=tck, tms=tms, tdi=tdi)

    def reset(self, *, trst, srst):
        print("Reset: trst:", trst, "srst:", srst)
        self.ll.reset(trst=trst, srst=srst)
