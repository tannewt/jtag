
class BoundMemoryArray:
    def __init__(self, dmi, start_address, length):
        self.dmi = dmi
        self.start_address = start_address
        self.length = length

    def __getitem__(self, index):
        return self.dmi[self.start_address + index]

    def __setitem__(self, index, value):
        self.dmi[self.start_address + index] = value

class MemoryArray:
    def __init__(self, start_address, length):
        self.start_address = start_address
        self.length = length

    def __get__(self, obj, objtype=None) -> None:
        bound = BoundMemoryArray(obj.dmi, self.start_address, self.length)
        setattr(obj, self.name, bound)
        return bound

    def __set_name__(self, owner, name):
        self.name = name

class Register:
    def __init__(self, address, wrapper=None):
        self.address = address
        self.wrapper = wrapper

    def __get__(self, obj, objtype=None) -> None:
        value = obj.dmi[self.address]
        if self.wrapper:
            return self.wrapper(value)
        return value

class RORegister(Register):
    pass

class ROBit:
    def __init__(self, bit_number):
        self.mask = 1 << bit_number

    def __get__(self, obj, objtype=None) -> bool:
        return (obj.value & self.mask) != 0

class PresetBit(ROBit):
    pass

class PresetBits:
    def __init__(
        self,
        num_bits,
        lowest_bit):
        self.bit_mask = ((1 << num_bits) - 1) << lowest_bit
        self.lowest_bit = lowest_bit

    def __get__(self, obj, objtype=None) -> None:
        v = obj.value
        return (v & self.bit_mask) >> self.lowest_bit

class DebugModuleStatus:
    impebreak = PresetBit(22)
    
    allhavereset = ROBit(19)
    anyhavereset = ROBit(18)

    allresumeack = ROBit(17)
    anyresumeack = ROBit(16)

    allnonexistent = ROBit(15)
    anynonexistent = ROBit(14)

    allunavail = ROBit(13)
    anyunavail = ROBit(12)

    allrunning = ROBit(11)
    anyrunning = ROBit(10)

    allhalted = ROBit(9)
    anyhalted = ROBit(8)

    authenticated = ROBit(7)
    authbusy = ROBit(6)

    hasresethaltreq = PresetBit(5)

    confstrptrvalid = PresetBit(4)

    version = PresetBits(4, 0)

    def __init__(self, value):
        self.value = value


class DebugModule:
    data = MemoryArray(0x04, 12)
    dmcontrol = Register(0x10)
    dmstatus = RORegister(0x11, DebugModuleStatus)
    hartinfo = Register(0x12)
    haltsum1 = Register(0x13)
    hawindowsel = Register(0x14)
    hawindow = Register(0x15)
    abstractcs = Register(0x16)
    command = Register(0x17)
    abstractauto = Register(0x18)
    confstrptr0 = Register(0x19)
    confstrptr1 = Register(0x1a)
    confstrptr2 = Register(0x1b)
    confstrptr3 = Register(0x1c)
    nextdm = Register(0x1d)
    progbuf = MemoryArray(0x20, 16)
    authdata = Register(0x30)
    haltsum2 = Register(0x34)
    haltsum3 = Register(0x35)
    sbaddress3 = Register(0x37)
    sbcs = Register(0x38)
    sbaddress0 = Register(0x39)
    sbaddress1 = Register(0x3a)
    sbaddress2 = Register(0x3b)
    sbdata = MemoryArray(0x3c, 4)
    haltsum0 = Register(0x40)

    def __init__(self, dmi: DebugModuleInterface):
        self.dmi = dmi


