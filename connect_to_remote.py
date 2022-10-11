import socket
import rbb_socket
import sys
import jtag

port = int(sys.argv[-1])

sock = socket.create_connection(("localhost", port))
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)

remote = rbb_socket.RemoteSocket(sock)

remote.blink_on()
remote.blink_off()

jtag_top = jtag.JTAG(remote)

sock.close()
