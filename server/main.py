import logging
import argparse
from server import Server

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", type=int, action='store', default=2010, help='the port that the server should listen on')
parser.add_argument("-n", "--host", type=str, action='store', default='::', help='the servers hostname')
parser.add_argument("-d", "--debug", action='store_true', help="debug mode")

args = parser.parse_args()
if __name__ == '__main__':
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    if args.port < 1:
        args.port = 6667

    server = Server()
    server.connect(args.host, args.port)
    server.listen()

