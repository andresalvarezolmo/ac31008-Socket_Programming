import socket
import sys

server = "127.0.0.1"
channel = "#hola"
botnick = "bot"

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# print("Connecting to: "+server)
# print("Connecting to: "+channel)
# print("Bot nick is: "+botnick)

irc.connect((server, 6667))
irc.send(("USER "+ botnick +" "+ botnick +" "+ botnick +" This is a fun  bot!\n").encode('utf-8'))
irc.send(("NICK "+ botnick +"\n").encode('utf-8'))
irc.send(("JOIN "+ channel +"\n").encode('utf-8'))
irc.send(("PRIVMSG #hola :HELLOWORLD\n").encode('utf-8'))

while 1:

   text=irc.recv(4096)
   # print("--------------------\n")
   # print(text.decode('utf-8'))
   # print("--------------------\n")
   if text.find('!hello'.encode('utf-8')) != -1:
      irc.send("PRIVMSG #hola :Hello User \r\n".encode('utf-8'))

   elif text.find('!slap'.encode('utf-8')) != -1:
      # irc.send("NAMES 127.0.0.1 \r\n".encode('utf-8'))
      irc.send("PRIVMSG #hola :got Slapped \r\n".encode('utf-8'))
   
   elif text.find('PRIVMSG bot :'.encode('utf-8')) != -1:
      parameters = text.split("!".encode("utf-8"))
      issuer = (parameters[0].decode("utf-8")).replace(':','')
      irc.send(("PRIVMSG " + issuer + "  :Random\r\n").encode('utf-8'))

   elif text.find('end'.encode('utf-8')) != -1:
      print('Connection closed')
      irc.close()
      break

   # if text.find(':!hi') !=-1:
   #    t = text.split(':!hi')
   #    to = t[1].strip()
   #    irc.send('PRIVMSG '+channel+' :Hello '+str(to)+'! \r\n')
