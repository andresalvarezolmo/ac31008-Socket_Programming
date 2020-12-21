class Channel:
    """
    Class to represent an IRC channel.
    Used to manage clients and send messages
    """

    def __init__(self, name, creator):
        self.clients = [creator]
        self.name = name
        self.topic = ''

    def join(self, client):
        self.clients.append(client)

    def client_str(self):
        clients = [c.nickname + " " for c in self.clients]
        return clients

    def braodcast(self, message, sender):
        """
        braodcast a message to every client socket in the channel, except to the sending socking
        :param message: the message that should be broadcasted
        :param sender: the client object that sends the message
        :return:
        """
        for c in self.clients:
            if c is sender:
                continue
            c.privmsg(sender.nickname, self.name, message)
