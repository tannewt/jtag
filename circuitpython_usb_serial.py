import usb_serial
import jtag
import sys
from adafruit_board_toolkit import circuitpython_serial

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

ll.blink_off()

ll.quit()
