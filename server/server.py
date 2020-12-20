import socket
import select
import logging
from client import Client

class Server:
    """
    Represents a server socket object.
    It's intended to be constantly listening to incoming connections
    """

    def __init__(self):
        self.server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # reuse port
        self.server.setblocking(False)
        self.inputs = [self.server]
        self.outputs = [] # not used
        self.errors = []
        self.clients = {}

    def connect(self, host, port=2020):
        """
        binds the server socket so that it is ready to receive connections
        :param host: the hostname, defaults to socket.gethostname()
        :param port: the port that the server should listen on, default is 2020
        :return: void
        """
        self.server.bind((host, port))
        self.server.listen()

    def listen(self):
        """
        Event handler that listens for incoming messages from client sockets
        :return: void
        """
        while self.inputs:
            readable, writeable, exceptional = select.select(self.inputs, self.outputs, self.errors)
            for s in readable:
                # handle new connections
                if s is self.server:
                    conn, addr = s.accept()
                    conn.setblocking(False)
                    self.inputs.append(conn)
                    self.clients[conn] = Client(conn, addr)
                # handle existing clients
                else:
                    data = s.recv(1024)
                    if data:
                        # parse message
                        print(f"connection data: {data}")
                        message = data.decode('utf-8').split()
                        logging.debug(message)

                        if len(message) < 1:
                            s.sendall(b'message to short\n\r')
                            continue

                        command = message[0].upper()

                        if command == 'NICK':
                            self.clients[s].set_nick(message[1])
                            logging.debug(f"set users nickname to {self.clients[s].nickname}")
                            logging.debug(self.clients)
                            s.sendall(b'NICK :)\n\r')
                        elif command == 'USER':
                            
                        else:
                            s.sendall('invalid or unknown message:\n\r'.encode())
                    # no data received, connection is closed
                    else:
                        self.inputs.remove(s)
                        del self.clients[s]
                        s.close()

