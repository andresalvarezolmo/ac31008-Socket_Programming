import socket
import select

class Server:
    """
    Represents a server socket object.
    It's intended to be constantly listening to incoming connections
    """

    def __init__(self):
        self.server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.server.setblocking(False)
        self.inputs = [self.server]
        self.outputs = []
        self.errors = []

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
                if s is self.server:
                    conn, addr = s.accept()
                    conn.setblocking(False)
                    self.inputs.append(conn)
                else:
                    data = s.recv(1024)
                    if data:
                        # echo
                        s.sendall(data)
                    else:
                        self.inputs.remove(s)
                        s.close()