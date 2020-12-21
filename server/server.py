import socket
import select
import logging
from client import Client
from channel import Channel

class Server:
    """
    Represents a server socket object.
    It's intended to be constantly listening to incoming connections
    """

    replies = {
        "WELCOME" : ("001", ":Welcome to our IRC server"),
        "ERR_NONICKNAMEGIVEN" : (431, ":No nickname given"),
        "ERR_NICKNAMEINUSE" : (433, "{} :Nickname is already in use"),
        "ERR_NEEDMOREPARAMS" : (461, "{} :Not enough parameters"),
        "ERR_ALREADYREGISTRED" : (462, ":You may not reregister"),
        "RPL_LUSERCLIENT" : (251, ":There are {} users and {} services on {} servers"),
        "ERR_NOMOTD" : (422, ":MOTD File is missing"),
        "ERR_NOSUCHCHANNEL": (403, "{} :No such channel"),
        "RPL_NOTOPIC": ("331", "{} :No topic set"),
        "RPL_NAMREPLY": (353, "= {} :{}"),
        "RPL_ENDOFNAMES": ("366", "{} :End of NAMES list"),
        "RPL_WHOREPLY": (352, "{}"),
        "ERR_NOSUCHNICK": (401, "{} :No such nick/channel")

    }
    crlf = '\r\n'

    def __init__(self):
        self.server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # reuse port
        self.server.setblocking(False)
        self.inputs = [self.server]
        self.outputs = [] # not used
        self.errors = []
        self.clients = {} # maps client sockets to client objects
        self.registered_clients = {} # maps a nickname to a client object
        self.channels = {} # maps a channel name to a Channel object
        self.commands = {
            "NICK": self.nick_msg,
            "USER": self.user_msg,
            "JOIN" : self.join_msg,
            "PRIVMSG" : self.privmsg_msg,
            "PING" : self.ping_msg,
            "NAMES" : self.names_msg
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
                if s is self.server:
                    conn, addr = s.accept()
                    logging.info("client connected: {}".format(addr))
                    conn.setblocking(False)
                    self.inputs.append(conn)
                    self.clients[conn] = Client(conn, addr)
                else:
                    data = s.recv(1024)
                    if data:
                        print(data)
                        messages = data.decode('utf-8').split('\r\n')
                        for m in messages:
                            reply = self.parse_client_message(self.clients[s], m)
                            s.sendall(reply.encode())

                    # no data received, connection is closed
                    else:
                        logging.debug(f"removing {s} from input pool")
                        self.inputs.remove(s)
                        for c in self.channels:
                            self.channels[c].remove_user(self.clients[s])
                        client = self.clients[s]
                        if client.nickname in self.registered_clients:
                            self.registered_clients.pop(client.nickname)
                        del self.clients[s]
                        s.close()

    def generate_reply(self, replycode, client=None, sender=None, args=""):
        """
        generates a server reply message based on the provided reply code
        :param replycode: the statuscode of the previous action
        :return: a reply message
        """
        msg = self.replies[replycode][1].format(*args)
        code = self.replies[replycode][0]
        nickname = ''
        if client and client.has_nick:
            nickname = client.nickname + " "

        if sender:
            prefix = f"{sender.nickname}"
        else:
            prefix = ":" + socket.gethostname()

        return f"{prefix} {code} {nickname}{msg} {Server.crlf}"

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
                return m.upper(), ""
            command = m[0:w].upper()
            column = m.find(':')
            if column > 0:
                text = m[column:]
                params = m[w:column].split()
                params.append(text)
            else:
                params = m[w:].split()
            return command, params
        return ""

    def parse_client_message(self, client, m):
        """
        takes an IRC message string send by client and performs the requested action based on the message
        :param client: the client object that corresponds to the sending connection socket (in the client directory)
        :param message: the message that was send, as a string
        :return: the reply that should be send to the client socket
        """

        if len(m) < 1:
            return ""
        command, params = self.parse_commnd(m)

        if command not in self.commands:
            logging.debug(f"[parse_client_message] unknown command: {command}")
            return ""
        logging.debug(f"[parse_client_message] params: {params}")
        reply = self.commands[command](client, params)
        return reply

    def nick_msg(self, client, params):
        if not params:
            return self.generate_reply('ERR_NONICKNAMEGIVEN')
        else:
            client.set_nick(params[0])
            if client.is_registered:
                self.welcome(client)
            return ""

    def user_msg(self, client, params):
        if len(params) != 4:
            return self.generate_reply('ERR_NEEDMOREPARAMS', args=('USER'))
        if client.is_registered:
            return self.generate_reply('ERR_ALREADYREGISTRED')

        client.register(params)
        if client.is_registered:
            self.welcome(client)
        return ""

    def join_msg(self, client, params):
        channel_name = params[0]
        if channel_name[0] != '#':
            return
        if channel_name in self.channels:
            self.channels[channel_name].join(client)
        else:
            new_channel = Channel(channel_name, client)
            self.channels[channel_name] = new_channel

        self.channels[channel_name].notify_join(client)
        client.sendmsg(f":{socket.gethostname()} 331 {client.nickname} {channel_name} :No topic set{self.crlf}")
        client.sendmsg(f":{socket.gethostname()} 353 {client.nickname} = {channel_name} :{self.channels[channel_name].client_str()}{self.crlf}")
        client.sendmsg(f":{socket.gethostname()} 366 {client.nickname} {channel_name} :End of NAMES list{self.crlf}")


        return ""

    def privmsg_msg(self, client, params):
        logging.debug(f"[privmsg_msg] params: {params}")

        receipient = params[0]
        text = params[1]

        if receipient[0] == '#':
            if receipient in self.channels:
                self.channels[receipient].broadcast(text, client)
            else:
                return self.generate_reply("ERR_NOSUCHNICK", args=(receipient))
        else:
            if receipient in self.registered_clients:
                self.registered_clients[receipient].privmsg(client, receipient, text)
            else:
                return self.generate_reply("ERR_NOSUCHNICK", args=(receipient))

        return ""

    def ping_msg(self, client, params):
        return f"PONG{self.crlf}"

    def names_msg(self, client, params):
        channel_name = params[0]
        if channel_name in self.channels:
            client.sendmsg(f":{socket.gethostname()} 353 {client.nickname} = {channel_name} :{self.channels[channel_name].client_str()}{self.crlf}")
        client.sendmsg(f":{socket.gethostname()} 366 {client.nickname} {channel_name} :End of NAMES list{self.crlf}")
        return ""

    def usercount(self):
        return len(self.registered_clients)

    def welcome(self, client):
        self.registered_clients[client.nickname] = client
        client.sendmsg(self.generate_reply("WELCOME", client=client))
        client.sendmsg(self.generate_reply("RPL_LUSERCLIENT",client=client, args=(self.usercount(),0,1)))
        client.sendmsg(self.generate_reply("ERR_NOMOTD", client=client))