
class Client:
    """
    represents a client object and provides functions to manipulate the user's information and to send messages
    to the client
    """
    def __init__(self, connection, address):
        self.socket = connection
        self.address = address
        self.nickname = '' # max 9 characters
        self.realname = ''
        self.username = ''
        self.is_registered = False
        self.has_userinfo = False
        self.has_nick = False

    def set_nick(self, nickname):
        """
        sets the nickname of this client
        :param nick: the clients nickname
        :return:
        """
        self.has_nick = True
        if self.has_userinfo:
            self.is_registered = True
        self.nickname = nickname

    def register(self, params):
        """
        registers personal information with self.
        Intended to be called by a function that handles a USER IRC message
        :param params: list consiting of username, hostname, servername and realname
        :return:
        """
        if len(params) != 4:
            return False
        if self.is_registered:
            return False
        self.has_userinfo = True
        if self.has_nick:
            self.is_registered = True
        self.username, self.hostname, self.servername, self.realname = params
        return True

    def privmsg(self, sender, recipient, message):
        """
        send a IRC PRIVMSG message to a user or channel
        :param sender: the message sender
        :param recipient: the recipient as a str, either a nickname or channel name
        :param message: the message to be send, prefixed with ":"
        :return: 
        """
        message = f":{sender.nickname}!{sender.username}@127.0.0.1 PRIVMSG {recipient} {message} \n\r"
        self.socket.sendall(message.encode())

    def sendmsg(self, message):
        """
        sends an arbitrary message to the client. The caller is responsible for ensuring that the message meets the IRC
        standard's syntax
        :param message: message to be send
        :return: void
        """
        self.socket.sendall(message.encode())