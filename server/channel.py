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

    def clients(self):
        clients = [c + " " for c in self.clients.nickname]
        return clients

    def braodcast(self, message, sender=None):
        """
        braodcast a message to every client socket in the channel, except to the sending socking
        :param message: the message that should be broadcasted
        :param sender: the client object that sends the message
        :return:
        """
        for c in self.clients:
            if c is sender:
                continue
            c.sendmsg(message)