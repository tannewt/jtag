import array

class TAP:
    def __init__(self, bus):
        self.bus = bus

class JTAG:
    def __init__(self, ll):
        self.ll = ll
        self.ll.write(tck=False, tms=False, tdi=False)
        self.reset()

        # Shift out DR
        self.select_dr()
        self.select_shift()

        all_bytes = array.array("B")
        ff_count = 0
        while ff_count < 4:
            b = self.read_byte()
            if b == 0xff:
                ff_count += 1
            else:
                ff_count = 0
            print(hex(b))
            all_bytes.append(b)
        print([hex(b) for b in all_bytes])

        self._shift_to_run()
        self.select_ir()
        self.select_shift()

        for i in range(8):
            b = self.read_byte()
            print(hex(b))


    def reset(self):
        self.ll.write(tck=False, tms=True, tdi=False)
        for i in range(5):
            self._send_tms_one()
        self.ll.write(tck=False, tms=False, tdi=False)
        self.ll.write(tck=True, tms=False, tdi=False)
        # Now in Run-Test/Idle
        self.ll.write(tck=False, tms=False, tdi=False)

    def _shift_to_run(self):
        self._send_tms_one() # to exit1
        self._send_tms_one() # to update
        self._send_tms_zero() # to run test/idle


    def _send_tms_one(self):
        self.ll.write(tck=False, tms=True, tdi=False)
        self.ll.write(tck=True, tms=True, tdi=False)

    def _send_tms_one(self):
        self.ll.write(tck=False, tms=True, tdi=False)
        self.ll.write(tck=True, tms=True, tdi=False)

    def _send_tms_zero(self):
        self.ll.write(tck=False, tms=False, tdi=False)
        self.ll.write(tck=True, tms=False, tdi=False)

    def _idle_bus(self):
        self.ll.write(tck=False, tms=False, tdi=False)

    def select_dr(self): # From run test / idle
        self._send_tms_one()
        self._idle_bus()

    def select_ir(self):
        for i in range(2):
            self._send_tms_one()
        self._idle_bus()

    def read_byte(self):
        v = 0
        self.ll.write(tck=False, tms=False, tdi=True)
        for i in range(8):
            if self.ll.read_tdo():
                v += 1 << i
            self.ll.write(tck=True, tms=False, tdi=True)
            self.ll.write(tck=False, tms=False, tdi=True)
        self._idle_bus()

        return v

    def write_byte(self, b):
        v = 0
        for i in range(8):
            self.ll.write(tck=False, tms=False, tdi=(b & (1 << i)) != 0)
            self.ll.write(tck=True, tms=False, tdi=False)
        self._idle_bus()

        return v

    def select_shift(self):
        self._send_tms_zero()
        self._send_tms_zero()