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

    def set_realname(self, realname):
        """
        Sets the real name of a client.
        :param realname: the clients real name
        :return: void
        """
        self.realname = realname

    def set_username(self, username):
        """
        Sets the user name of a client.
        :param username: the clients user name
        :return: void
        """
        self.username = username