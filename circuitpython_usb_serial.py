import usb_serial
import jtag
import sys
from adafruit_board_toolkit import circuitpython_serial
import riscv_jtag_dtm

ports = circuitpython_serial.data_comports()

print(ports)

if not ports:
    sys.exit(1)

device = None
for p in ports:
    print(p, p.device)
    device = p.device


ll = usb_serial.USBSerialEncoder(device)

ll.blink_on()
jtag_top = jtag.JTAG(ll)

riscv_dm = riscv_jtag_dtm.JTAG_DTM(jtag_top.taps[0], ir_dtmcs=0x32, ir_dmi=0x38)

print("dtmcs", hex(riscv_dm.dtmcs))

print(hex(riscv_dm[0x12]))
print(hex(riscv_dm[0x11]))

ll.blink_off()

ll.quit()
