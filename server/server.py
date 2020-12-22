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

    def connect(self, host=socket.gethostname(), port=2010):
        """
        binds the server socket so that it is ready to receive connections.
        Intended to be called before listen()
        :param host: the hostname, defaults to socket.gethostname()
        :param port: the port that the server should listen on, default is 2010
        :return: void
        """
        self.server.bind((host, port))
        self.server.listen()

    def listen(self):
        """
        Event handler that listens for incoming messages from client sockets and then performs actions based
        on incoming messages.
        Intended to be called after connect()
        :return: void
        """
        while self.inputs:
            readable, _, exceptional = select.select(self.inputs, (), self.errors)
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
        generates a server reply message based on the provided reply code.
        The reply message has the form <prefix> <numberical code> <nickname> <message>
        :param replycode: the statuscode
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
        takes in a command string and returns a tuple containing the command and all parameters in a separate tuble.
        The entire text after the last : will be put into the same item
        :param command: command to be parsed
        :return: a tuple containing the command and a tupble of parameters and text
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
        takes an IRC message string, performs all necessary actions and returns a string that is intended to be send back
        to the client. This does not exclude however that this function is able to send messages directly to sockets if
        this is necessary
        :param client: the client object that corresponds to the sending connection socket (in the client directory)
        :param message: a single message that was send. (If more than one message is received sumultaneously, the calling
        function is responsible for splitting the string into atomic messages)
        :return: the reply that should be send to the client socket
        """

        if len(m) < 1:
            return ""
        command, params = self.parse_commnd(m)

        if command not in self.commands:
            logging.debug(f"[parse_client_message] unknown command: {command}")
            return ""
        reply = self.commands[command](client, params)
        return reply

    def nick_msg(self, client, params):
        """
        sets the nickname of client to params[0].
        :param client:
        :param params: a tuple with the nickname as its only argument
        :return: error message or empty string if successful
        """
        # TODO verify nickname vilidity (no #, no duplicates)
        if not params:
            return self.generate_reply('ERR_NONICKNAMEGIVEN')
        else:
            client.set_nick(params[0])
            if client.is_registered:
                self.welcome(client)
            return ""

    def user_msg(self, client, params):
        """
        sets the user information of the client object
        :param client: the sending client object
        :param params: a list containing username, hostname, sername, realname
        :return: error message or empty string if successful
        """
        if len(params) != 4:
            return self.generate_reply('ERR_NEEDMOREPARAMS', args=('USER'))
        if client.is_registered:
            return self.generate_reply('ERR_ALREADYREGISTRED')

        client.register(params)
        if client.is_registered:
            self.welcome(client)
        return ""

    def join_msg(self, client, params):
        """
        lets a client join a channel params[0]
        :param client:  the client object that should join the channel
        :param params: a list that contains the channel to be joined as its only item
        :return: error message or empty string if successful
        """
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
        """
        sends a private message (params[1]) from client to a recipient (params[0])
        :param client: the sender
        :param params: a list containing the recipient and the message text as its only items
        :return: error message or empty string if successful
        """
        recipient = params[0]
        text = params[1]

        if recipient[0] == '#':
            if recipient in self.channels:
                self.channels[recipient].broadcast(text, client)
            else:
                return self.generate_reply("ERR_NOSUCHNICK", args=(recipient))
        else:
            if recipient in self.registered_clients:
                self.registered_clients[recipient].privmsg(client, recipient, text)
            else:
                return self.generate_reply("ERR_NOSUCHNICK", args=(recipient))

        return ""

    def ping_msg(self, client, params):
        """
        sends a PONG message back to the client
        :param client: the client object that made the ping request
        :param params: PING parameters
        :return: error message or empty string if successful
        """
        return f":{socket.gethostname()} PONG {socket.gethostname()} :{params[0]} {self.crlf}"

    def names_msg(self, client, params):
        """
        sends a list of users that joined the channel params[0]
        :param client: the client that made the request
        :param params: the channel of which the usernames are requested
        :return: error message or empty string if successful
        """
        channel_name = params[0]
        if channel_name in self.channels:
            client.sendmsg(f":{socket.gethostname()} 353 {client.nickname} = {channel_name} :{self.channels[channel_name].client_str()}{self.crlf}")
        client.sendmsg(f":{socket.gethostname()} 366 {client.nickname} {channel_name} :End of NAMES list{self.crlf}")
        return ""

    def usercount(self):
        """
        counts the number of registered users
        :return: number of users on this server
        """
        return len(self.registered_clients)

    def welcome(self, client):
        """
        sends a welcome message to client
        :param client: the recipient of the welcome message
        :return: void
        """
        self.registered_clients[client.nickname] = client
        client.sendmsg(self.generate_reply("WELCOME", client=client))
        client.sendmsg(self.generate_reply("RPL_LUSERCLIENT",client=client, args=(self.usercount(),0,1)))
        client.sendmsg(self.generate_reply("ERR_NOMOTD", client=client))