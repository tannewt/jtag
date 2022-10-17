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

    def __init__(self, tap):
        self.tap = tap
        self.dtmcs_buf = bytearray(4)

        self.dmi_len = self.dtmcs_abits + 34

        dmi_bytes = self.dmi_len // 8 + (1 if self.dmi_len % 8 > 0 else 0)
        self.dmi_buf = bytearray(dmi_bytes)

    @property
    def dtmcs(self):
        self.tap.ir = 0x10
        self.tap.read_dr_into(self.dtmcs_buf)
        return struct.unpack("<I", self.dtmcs_buf)[0]

    def __getitem__(self, addr):
        self.tap.ir = 0x11
        self.tap.read_dr_into(self.dmi_buf, bitcount=self.dmi_len)
        return bytes(self.dmi_buf)

    def __setitem__(self, addr, value):
        pass

    def __len__(self):
        return 1 << self.dtmcs_abits
