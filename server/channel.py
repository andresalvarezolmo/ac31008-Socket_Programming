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
