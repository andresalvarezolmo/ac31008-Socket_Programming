import socket
import select
import logging
from client import Client
import selectors

# localhost
HOST = '127.0.0.1'
# port to listen on
PORT = 65432 

sel = selectors.DefaultSelector()
lsock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
lsock.bind((HOST, PORT))
lsock.listen()
print('listening on', (HOST, PORT))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

while True:
    events = sel.select(timeout=None)
    for key, mask in events:
        if key.data is None:
            accept_wrapper(key.fileobj)
        else:
            service_connection(key, mask)

def accept_wrapper(socket):
    """
    Accepts a new connection coming into the server.
    :param socket: socket of the incoming connection
    :return: void
    """
    # Should be ready to read
    conn, addr = socket.accept()
    print('accepted connection from', addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    """
    Servicing an already accepted connection.
    :param key: contains the socket object and data object
    :param mask: contains the events that are ready
    :return: void
    """
    socket = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        # Should be ready to read
        recv_data = socket.recv(1024)
        if recv_data:
            data.outb += recv_data
        else:
            print('closing connection to', data.addr)
            sel.unregister(socket)
            socket.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print('echoing', repr(data.outb), 'to', data.addr)
            # Should be ready to write
            sent = socket.send(data.outb)
            data.outb = data.outb[sent:]