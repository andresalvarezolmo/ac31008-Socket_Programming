import socket
import select
import logging
from client import Client

class Server:
    """
    Represents a server socket object.
    It's intended to be constantly listening to incoming connections
    """

    replies = {
        "ERR_NONICKNAMEGIVEN" : (431, ":No nickname given"),
        "ERR_NICKNAMEINUSE" : (433, "{} :Nickname is already in use")
    }

    crlf = '\n\r'

    def __init__(self):
        self.server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # reuse port
        self.server.setblocking(False)
        self.inputs = [self.server]
        self.outputs = [] # not used
        self.errors = []
        self.clients = {}
        self.commands = {
            "NICK": self.nick_msg,
            "USER": self.user_msg,
            "JOIN" : self.join_msg,
            "PRIVMSG" : self.privmsg_msg
        }

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
                    logging.debug("[server.listen] client with address {} connected".format(addr))
                    conn.setblocking(False)
                    self.inputs.append(conn)
                    self.clients[conn] = Client(conn, addr)
                # handle existing clients
                else:
                    data = s.recv(1024)
                    if data:
                        logging.debug(f"[listen] data: {data}")
                        reply = self.parse_client_message(client=self.clients[s], message=data.decode('utf-8'))
                        s.sendall(reply.encode())

                    # no data received, connection is closed
                    else:
                        self.inputs.remove(s)
                        del self.clients[s]
                        s.close()

    def get_prefix(self, client):
        """
        assembles an IRC prefix for a server-side reply message based on the given client object
        :return: prefix
        """
        # TODO make the prefix generation dynamic, maybe move and rename function
        return ':bjarne-lt'


    def generate_reply(self, client, replycode, args=""):
        """
        generates a server reply message based on the provided reply code
        :param replycode: the statuscode of the previous action
        :return: a reply message
        """
        msg = self.replies[replycode][1].format(*args)
        r = f"{self.replies[replycode][0]} {msg}"
        return f"{self.get_prefix(client)} {r} {Server.crlf}"

    def parse_commnd(self, m):
        """
        takes in a command string as send from a client and returns a tuple containing the command, the parameters as a
        tuple and the text
        :param command: command given
        :return: a tuple containing the command, the parameters and the text
        """
        if m:
            w = m.find(' ')
            if w < 0:
                return m.upper(), "", ""
            command = m[0:w].upper()
            column = m.find(':')
            text = ''
            if column > 0:
                logging.debug('c')
                text = m[column:]
                params = m[w:column].split()
            else:
                params = m[w:].split()
            return command, params, text
        return ""

    def parse_client_message(self, client, message):
        """
        takes an IRC message string send by client and performs the requested action based on the message
        :param client: the client object that corresponds to the sending connection socket (in the client directory)
        :param message: the message that was send, as a string
        :return: the reply that should be send to the client socket
        """
        messages = message.split('\r\n')
        logging.debug(f"[parse_client_message] messages: {messages}")
        for m in messages:
            logging.debug(f"[parse_client_message] parse_command={self.parse_commnd(m)}")
            if len(m) < 1:
                return ""
            command, params, text = self.parse_commnd(m)

            if command not in self.commands:
                logging.debug(f"parse_client_message] command {command} is not in commands dictionary")
                return ""
            reply = self.commands[command](client, params)
            return reply

    def nick_msg(self, client, params):
        if not params:
            return self.generate_reply(client, 'ERR_NONICKNAMEGIVEN')
        else:
            client.set_nick(params[0])
            return ""

    def user_msg(self, client, username, hostname, servername, realname):
        pass

    def join_msg(self, channel):
        pass

    def privmsg_msg(self, params):
        pass