import struct

class RegisterBits:
    def __set_name__(self, owner, name):
        self.register_name = name.split("_", maxsplit=1)[0]
        if not hasattr(owner, self.register_name):
            raise RuntimeError(f"Missing base register {self.register_name} for {name} bits.")


class W1Bit(RegisterBits):
    def __init__(
        self,
        bit: int,
    ) -> None:
        self.bit_mask = 1 << bit

    def __set__(self, obj, value: bool) -> None:
        if not value:
            raise ValueError("Write 1 bit")
        setattr(obj, self.register_name, self.bit_mask)

class FixedBits(RegisterBits):
    def __init__(
        self,
        num_bits,
        lowest_bit):
        self.bit_mask = ((1 << num_bits) - 1) << lowest_bit
        self.lowest_bit = lowest_bit

    def __get__(self, obj, objtype=None) -> None:
        if not hasattr(obj, "FixedBits"):
            setattr(obj, "FixedBits", {})
        cache = getattr(obj, "FixedBits")
        if self.register_name not in cache:
            cache[self.register_name] = getattr(obj, self.register_name)
        return (cache[self.register_name] & self.bit_mask) >> self.lowest_bit


class ROBits(RegisterBits):
    def __init__(
        self,
        num_bits,
        lowest_bit):
        self.bit_mask = ((1 << num_bits) - 1) << lowest_bit
        self.lowest_bit = lowest_bit

    def __get__(self, obj, objtype=None) -> None:
        v = getattr(obj, self.register_name)
        return (v & self.bit_mask) >> self.lowest_bit

class JTAG_DTM: # Implements DebugModuleInterface (aka bus)
    dtmcs_dmihardreset = W1Bit(17)
    dtmcs_dmireset = W1Bit(16)
    dtmcs_idle = FixedBits(3, 12)
    dtmcs_dmistat = ROBits(2, 10)
    dtmcs_abits = FixedBits(6, 4)
    dtmcs_version = FixedBits(4, 0)

    OP_IGNORE = 0x0
    OP_READ = 0x1
    OP_WRITE = 0x2
    OP_RESERVED = 0x3

    OP_STATUS_OK = 0x0
    OP_STATUS_RESERVED = 0x1
    OP_STATUS_FAILED = 0x2
    OP_STATUS_IGNORED = 0x3

    def __init__(self, tap, *, ir_dtmcs=0x10, ir_dmi=0x11):
        self.tap = tap
        self.ir_dtmcs = ir_dtmcs
        self.ir_dmi = ir_dmi
        self.dtmcs_buf = bytearray(4)

        self.dmi_len = self.dtmcs_abits + 34

        print(self.dtmcs_abits, self.dtmcs_idle)

        dmi_bytes = self.dmi_len // 8 + (1 if self.dmi_len % 8 > 0 else 0)
        self.dmi_buf = bytearray(dmi_bytes)

    @property
    def dtmcs(self):
        self.tap.ir = self.ir_dtmcs
        self.tap.read_dr_into(self.dtmcs_buf)
        return struct.unpack("<I", self.dtmcs_buf)[0]

    @dtmcs.setter
    def dtmcs(self, value):
        self.tap.ir = self.ir_dtmcs
        struct.pack_into("<I", self.dtmcs_buf, 0, value)
        self.tap.write_dr(value)

    def _unpack_dmi(self, buf):
        op = buf[0] & 0x03
        data = buf[0] >> 2
        data |= buf[1] << 6
        data |= buf[2] << 14
        data |= buf[3] << 22
        data |= (buf[4] & 0x03) << 30
        address = buf[4] >> 2
        offset = 6
        i = 5
        remaining_bits = self.dtmcs_abits - offset
        while remaining_bits > 0:
            bits = min(8, remaining_bits)
            address |= (buf[i] & ((1 << bits) - 1)) << offset
            i += 1
            remaining_bits -= bits
            offset += bits
        return address, data, op

    def _pack_dmi(self, address, data, op, buf):
        print(hex(address), hex(address << 2), hex(data), hex(op))
        buf[0] = op
        buf[0] |= (data & 0x3f) << 2
        buf[1] = (data >> 6) & 0xff
        buf[2] = (data >> 14) & 0xff
        buf[3] = (data >> 22) & 0xff
        buf[4] = (data >> 30) & 0x03
        buf[4] |= (address & 0x3f) << 2
        offset = 6
        i = 5
        remaining_bits = self.dtmcs_abits - offset
        while remaining_bits > 0:
            bits = min(8, remaining_bits)
            buf[i] = (address >> offset) & 0xff
            i += 1
            remaining_bits -= bits
            offset += bits

    def _run_transaction(self, addr, op, value=0):
        self.tap.ir = self.ir_dmi
        self._pack_dmi(addr, value, op, self.dmi_buf)
        self.tap.write_dr(self.dmi_buf, dr_len=self.dmi_len)
        for i in range(self.dtmcs_idle + 2):
            self.tap.idle_clock()
        self.tap.read_dr_into(self.dmi_buf, dr_len=self.dmi_len)
        _, data, op = self._unpack_dmi(self.dmi_buf)
        
        if op != 0:
            self.dtmcs_dmireset = True
            raise RuntimeError("Operation failed")

        return data


    def __getitem__(self, addr):
        return self._run_transaction(addr, JTAG_DTM.OP_READ)

    def __setitem__(self, addr, value):
        self._run_transaction(addr, JTAG_DTM.OP_WRITE, value)
    
    def __len__(self):
        return 1 << self.dtmcs_abits
