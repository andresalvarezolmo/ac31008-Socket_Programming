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

    def set_nick(self, nickname):
        """
        sets the nickname of this client
        :param nick: the clients nickname
        :return:
        """
        self.nickname = nickname