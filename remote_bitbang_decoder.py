# We use ints for the characters instead of strings to avoid allocations in
# MicroPython and CircuitPython.

class RemoteBitbangDecoder:
    def __init__(self, ll: LowLevelJTAG):
        self.ll = ll
        self.function_mapping = {
            66: ll.blink_on, # B
            98: ll.blink_off, # b
            81: ll.quit, # Q
            48: lambda: ll.write(tck=False, tms=False, tdi=False), # 0
            49: lambda: ll.write(tck=False, tms=False, tdi=True), # 1
            50: lambda: ll.write(tck=False, tms=True,  tdi=False), # 2
            51: lambda: ll.write(tck=False, tms=True,  tdi=True), # 3
            52: lambda: ll.write(tck=True,  tms=False, tdi=False), # 4
            53: lambda: ll.write(tck=True,  tms=False, tdi=True), # 5
            54: lambda: ll.write(tck=True,  tms=True,  tdi=False), # 6
            55: lambda: ll.write(tck=True,  tms=True,  tdi=True), # 7
            114: lambda: ll.reset(trst=False, srst=False), # r
            115: lambda: ll.reset(trst=False, srst=True), # s
            116: lambda: ll.reset(trst=True,  srst=False), # t
            117: lambda: ll.reset(trst=True,  srst=True), # u
        }

    def run_function(c: int) -> Optional[int]:
        if c == 82:
            return 49 if self.ll.read_tdo() else 48
        if c not in self.function_mapping:
            raise RuntimeError("Unknown function")
        self.function_mapping[c]()
        return None
