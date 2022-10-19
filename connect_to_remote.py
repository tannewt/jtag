import socket
import rbb_socket
import sys
import jtag

import jtag_debug
import riscv_jtag_dtm

port = int(sys.argv[-1])

sock = socket.create_connection(("localhost", port))
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)

remote = rbb_socket.RemoteSocket(sock)

remote.blink_on()
remote.blink_off()

jtag_top = jtag.JTAG(remote)

riscv_dm = riscv_jtag_dtm.JTAG_DTM(jtag_top.taps[0])

print(hex(riscv_dm[0x12]))
print(hex(riscv_dm[0x11]))


sock.close()
