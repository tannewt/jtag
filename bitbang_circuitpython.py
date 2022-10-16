from digitalio import DigitalInOut


class BitBangJTAG(LowLevelJTAG):
    def __init__(self, *, tck:DigitalInOut, tms: DigitalInOut, tdi: DigitalInOut, tdo: DigitalInOut,
                 trst: DigitalInOut, srst: DigitalInOut=None, blink: DigitalInOut=None):
        self.tck = tck
        self.tms = tms
        self.tdi = tdi
        self.tdo = tdo
        self.trst = trst
        self.srst = srst
        self.blink = blink

    def blink_on(self) -> None:
        if self.blink:
            self.blink.value = True

    def blink_off(self) -> None:
        if self.blink:
            self.blink.value = False

    def read_tdo(self) -> bool:
        return self.tdo.value

    def quit(self) -> None:
        self.tck.deinit()
        self.tms.deinit()
        self.tdi.deinit()
        self.tdo.deinit()
        self.trst.deinit()
        if self.srst:
            self.srst.deinit()
        if self.blink:
            self.blink.deinit()

    def write(self, *, tck: bool, tms: bool, tdi: bool) -> None:
        self.tms.value = tms
        self.tdi.value = tdi
        self.tck.value = tck

    def reset(self, *, trst: bool, srst: bool) -> None:
        self.trst.value = trst
        if self.srst:
            self.srst.value = srst
