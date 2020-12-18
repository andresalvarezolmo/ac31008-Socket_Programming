import socket
import sys

server = "127.0.0.1"
channel = "#"
botnick = "bot"

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Connecting to:"+server)
irc.connect((server, 6667))
irc.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :This is a fun  bot!\n")
irc.send("NICK "+ botnick +"\n")
irc.send("PRIVMSG nickserv :iNOOPE\r\n")
irc.send("JOIN "+ channel +"\n")

while 1:

   text=irc.recv(2040)
   print(text)
#    if text.find('PING') != -1:
#       irc.send('PONG ' + text.split() [1] + '\r\n')
#    if text.find(':!hi') !=-1:
#       t = text.split(':!hi')
#       to = t[1].strip()
#       irc.send('PRIVMSG '+channel+' :Hello '+str(to)+'! \r\n')
