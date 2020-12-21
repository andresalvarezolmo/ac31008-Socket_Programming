
class Client:
    """
    represents a client object
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
        if len(params) != 4:
            return False
        if self.is_registered:
            return False
        self.has_userinfo = True
        if self.has_nick:
            self.is_registered = True
        self.username, self.hostname, self.sername, self.realname = params
        return True

    def sendmsg(self, message):
        self.socket.sendall(message.encode())