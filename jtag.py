import array
import struct

class TAP:
    def __init__(self, bus, idcode, irlen, *, irlen_offset=0):
        self.bus = bus
        self.idcode = idcode
        self.irlen = irlen
        self.irlen_offset = irlen_offset
        self.ir_mask = (1 << self.irlen) - 1

    @property
    def ir(self):
        self.bus.select_ir()
        self.bus.select_shift()
        b = self.bus.read_byte()
        self.bus._shift_to_run()
        return b & self.ir_mask

    @ir.setter
    def ir(self, value):
        self.bus.select_ir()
        self.bus.select_shift()
        # TODO: shift out offset bits
        self.bus.write(value, bitcount=self.irlen)

    def read_dr_into(self, buf, *, dr_len=None):
        if dr_len is None:
            dr_len = len(buf) * 8

        self.bus.select_dr()
        self.bus.select_shift()
        # TODO: Handle bypass DR bits for other devices.
        dr_bytes = dr_len // 8 + (1 if dr_len % 8 > 0 else 0)
        for i in range(dr_bytes):
            buf[i] = self.bus.read_byte(tdi=False)
        self.bus._shift_to_run()

class JTAG:
    def __init__(self, ll):
        self.ll = ll
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
        # ID Codes
        print([hex(b) for b in all_bytes])

        self._shift_to_run()
        self.select_ir()
        self.select_shift()

        # Default instruction register values and transistion to bypass
        for i in range(8):
            b = self.read_byte()
            print(hex(b))

        # In bypass mode now.
        self._shift_to_run()

        self.select_dr()
        self.select_shift()
        # Send 8 1s while we read.
        self.read_byte()
        # Send a zero
        self.ll.write(tck=False, tms=False, tdi=False)
        self.ll.write(tck=True, tms=False, tdi=False)
        device_count = 1
        self.ll.write(tck=False, tms=False, tdi=True)
        while self.ll.read_tdo():
            self.ll.write(tck=True, tms=False, tdi=True)
            self.ll.write(tck=False, tms=False, tdi=True)
            device_count += 1
        self.ll.write(tck=True, tms=False, tdi=False)
        self._shift_to_run()
        print(device_count, "devices")

        irlen_offset = 0
        self.taps = []
        for device in range(device_count):
            idcode = struct.unpack_from("<I", all_bytes, offset=device*4)[0]
            print(hex(idcode))
            # TODO: Find a plugin that matches the idcode. We need the irlen. 
            self.taps.append(TAP(self, idcode, 5))


    def reset(self):
        for i in range(5):
            self._send_tms_one()
        self.ll.write(tck=False, tms=False, tdi=False)
        self.ll.write(tck=True, tms=False, tdi=False)
        # Now in Run-Test/Idle

    def _shift_to_run(self):
        self._send_tms_one() # to exit1
        self._send_tms_one() # to update
        self._send_tms_zero() # to run test/idle


    def _send_tms_one(self):
        self.ll.write(tck=False, tms=True, tdi=True)
        self.ll.write(tck=True, tms=True, tdi=True)

    def _send_tms_zero(self):
        self.ll.write(tck=False, tms=False, tdi=True)
        self.ll.write(tck=True, tms=False, tdi=True)

    def select_dr(self): # From run test / idle
        self._send_tms_one()

    def select_ir(self):
        for i in range(2):
            self._send_tms_one()

    def read_byte(self, *, tdi=True):
        v = 0
        self.ll.write(tck=False, tms=False, tdi=tdi)
        for i in range(8):
            if self.ll.read_tdo():
                v += 1 << i
            self.ll.write(tck=True, tms=False, tdi=tdi)
            if i < 7:
                self.ll.write(tck=False, tms=False, tdi=tdi)

        return v

    def write(self, b, *, bitcount=8):
        for i in range(bitcount):
            bit = (b & (1 << i)) != 0
            last_bit = i == bitcount - 1
            self.ll.write(tck=False, tms=i==last_bit, tdi=bit)
            self.ll.write(tck=True, tms=last_bit, tdi=bit)
        self._send_tms_one() # to update
        self._send_tms_zero() # to run test/idle

    def select_shift(self):
        self._send_tms_zero()
        self._send_tms_zero()