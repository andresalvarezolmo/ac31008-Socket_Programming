#!/usr/bin/python3
import socket
import random

#the socket we’ll be using to connect and communicate with the IRC server. 
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#name of the server and channel we’ll be connecting to
server = "127.0.0.1" # Server
channel = "#testing" # Channel

botnick = "bot1234" #bot's name
adminname = "Raffa12" #IRC nickname, can send administrative commands to the bot and an exit code to look for to end the bot 
exitcode = "bye " + botnick #text to exit
afile = 'facts.txt' #file saving thr random facts available

ircsock.connect((server, 6667)) # Here we connect to the server using the port 6667

#send some information to let the server know who we are. 
ircsock.send(bytes("USER "+ botnick +" "+ botnick +" "+ botnick + " " + botnick + "\n", "UTF-8")) # user information
ircsock.send(bytes("NICK "+ botnick +"\n", "UTF-8")) # assign the nick to the bot

# function to join a channel, pass name 
def joinchan(chan):
  #send the message to IRC as UTF-8 encoded bytes
  ircsock.send(bytes("JOIN "+ chan +"\n", "UTF-8")) 
  #ircmsg = ""
  #while ircmsg.find("End of /NAMES list.") == -1: #loop to continually check for and receive new info from server until we get a message with ‘End of /NAMES list.’
  #  ircmsg = ircsock.recv(2048).decode("UTF-8")
  #  ircmsg = ircmsg.strip('\n\r')
  #  print(ircmsg)

#respond with "PONG :pingis" to any PING 
def ping():
  ircsock.send(bytes("PONG :pingis\n", "UTF-8"))

#send message to target 
#We will assume we are sending to the channel by default if no target is defined. 
#Using target=channel in the parameters section says if the function is called without a target defined
def sendmsg(msg, target):
  ircsock.send(bytes("PRIVMSG "+ target +" :"+ msg +"\n", "UTF-8"))

#TODO
#send a picture in the chat
def sendpic(msg, target=channel):
  ircsock.send(bytes("PRIVMSG "+ target +" :"+ msg +"\n", "UTF-8"))

#read random line from file
def random_line(filename):
  lines = open(filename).read().splitlines()
  return random.choice(lines)

#call the other functions as necessary and process the information received from IRC and determine what to do with it.
def main():
  
  joinchan(channel) #join the channel

  #infinite loop to continually check for and receive new info from server. This ensures our connection stays open. 
  while 1:

    #receiving information from the IRC server
    ircmsg = ircsock.recv(2048).decode("UTF-8")

    #remove any line break characters from the string. 
    ircmsg = ircmsg.strip('\n\r')
    #debugging: print the received information to your terminal.
    print(ircmsg)

    #check if the information we received was standard messages in the channel 
    if ircmsg.find("PRIVMSG") != -1:
      #get name of the person who sent the message. 
      #Messages come in from from IRC in the format of ":[Nick]!~[hostname]@[IP Address] PRIVMSG [channel] :[message]”
      name = ircmsg.split('!',1)[0][1:]
      message = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1]
      origin = ircmsg.split('PRIVMSG ',1)[1].split(' ', 1)[0]

      if len(name) < 17: #check valid user

        if origin.lower() == channel.lower():

          #check for hello message
          if message.find('Hi ' + botnick) != -1:
            sendmsg("Hello " + name + "!", channel)

          #check for !hello message
          if message.find('!hello') != -1:
            sendmsg("Hello " + name + "!", channel)
        
          #check for reqeust for fact
          if message.find('!fact') != -1:
            fact = random_line(afile)
            sendmsg(fact, channel)

          #check for reqeust for fact
          if message.find('!slap') != -1:
            sendpic("*** SLAPPED ***", channel)
          
          #check for a ‘code’ at the beginning of a message and parse it to do a complex task. 
          #".tell [target] [message]” 
          if message[:5].find('.tell') != -1:
            target = message.split(' ', 1)[1]  #split the command from the rest of the message.
            if target.find(' ') != -1: #split full message incl spaces
                message = target.split(' ', 1)[1]
                target = target.split(' ')[0]

            #wrong input
            else:
              #target to the name of the user who sent the message (parsed from above)
              target = name
              message = "Could not parse. The message should be in the format of ‘.tell [target] [message]’ to work properly."
            
            sendmsg(message, target)

          #to exit bot
          #if name.lower() == adminname.lower() and message.rstrip() == exitcode:
          #  sendmsg("oh...okay. :'(", channel)
          #  ircsock.send(bytes("QUIT \n", "UTF-8")) #quit command to IRC server 
          #  return

          #to exit bot
          if message.rstrip() == exitcode:
            sendmsg("oh...okay. :'(", channel)
            ircsock.send(bytes("QUIT \n", "UTF-8")) #quit command to IRC server 
            return

        
        #if message from private channel
        if origin.lower() == botnick.lower():
           
          #send fact after every message
          if message != -1:
            fact = random_line(afile)
            sendmsg(fact, name)

    #if message not a PRIVMSG
    else:
      #if PING request respond with PONG
      if ircmsg.find("PING :") != -1:
        ping()

#start program
main()