import logging
class Channel:
    """
    Class to represent an IRC channel.
    Provides functions to manipulate the channel
    """

    def __init__(self, name, creator):
        self.clients = [creator]
        self.name = name
        self.topic = ''

    def join(self, client):
        """
        add client to the list of joined clients
        :param client: the client to join this channel
        :return:
        """
        if client not in self.clients:
            self.clients.append(client)
            for c in self.clients:
                c.sendmsg(f":{client.nickname}!{client.username}@127.0.0.1 JOIN {self.name}\n\r")

    def client_str(self):
        """
        return a whitespace separated list of all clients that are in a specific channel
        :return:
        """
        clients = ""
        for c in self.clients:
            clients += c.nickname + " "
        return clients

    def broadcast(self, message, sender):
        """
        braodcast a message to every client socket in the channel, except to the sending socking
        :param message: the message that should be broadcasted
        :param sender: the client object that sends the message
        :return:
        """
        for c in self.clients:
            if c is sender:
                continue
            logging.debug(f"in channel.braodcast: {c.nickname} - {c.socket}")
            c.privmsg(sender, self.name, message)

    def remove_user(self, to_remove):
        """
        removes to_remove from this channel
        :param to_remove:
        :return:
        """
        if to_remove in self.clients:
            self.clients.remove(to_remove)
            logging.debug(f"in channel.remove_user: removed socket {to_remove} from channel")