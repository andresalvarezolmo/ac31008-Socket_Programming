#!/usr/bin/python3
import socket
import random

#the socket we’ll be using to connect and communicate with the IRC server.
 
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #to connect using ipv4 server
# ircsock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM) #to connect using ipv6 server
#name of the server and channel we’ll be connecting to
server = "127.0.0.1" # Server localhost ipv4
# server = "::1" # Server localhost ipv6
# server = "fc00:1337::19" # Actual ipv6 Server that will be used for marking

channel = "#testing" # Channel

botnick = "BOT" #bot's name
adminname = "ABC" #IRC nickname to send admin commands to the bot
exitcode = "Bye " + botnick #text to exit
afile = 'facts.txt' #file saving thr random facts available
users = [] #list with all users on the channel
user = "user"

try:
  ircsock.connect((server, 6667)) # Here we connect to the server using the port 6667
except:
  print("ERROR: Could not connect to server: " + server)

try:
  #send some information to let the server know who we are. 
  ircsock.send(bytes("USER "+ botnick +" "+ botnick +" "+ botnick + " " + botnick + "\n", "UTF-8")) # user information
  ircsock.send(bytes("NICK "+ botnick +"\n", "UTF-8")) # assign the nick to the bot
except:
  print("ERROR: Could not send to server: " + server)

# function to join a channel, pass name 
def joinchan(chan):
  #send the message to IRC as UTF-8 encoded bytes
  try:
    ircsock.send(bytes("JOIN "+ chan +"\n", "UTF-8")) 
  except:
    print("ERROR: Could not join channel: " + chan)

  #ircmsg = ""
  #while ircmsg.find("End of /NAMES list.") == -1: #loop to continually check for and receive new info from server until we get a message with ‘End of /NAMES list.’
  #  ircmsg = ircsock.recv(2048).decode("UTF-8")
  #  ircmsg = ircmsg.strip('\n\r')
  
  

#respond with "PONG :pingis" to any PING 
def ping():
  try:
    ircsock.send(bytes("PONG :pingis\n", "UTF-8"))
  except:
    print("ERROR: Could not send pong!")



#send message to target 
def sendmsg(msg, target):
  try:
    ircsock.send(bytes("PRIVMSG "+ target +" :"+ msg +"\n", "UTF-8"))
  except:
    print("ERROR: Could not send message to: " + target)



#get a list of all users in channel and return random one
def randomuser():
  #get a list of all users on channel

  ircsock.send(bytes("NAMES " + channel + "\r\n", "UTF-8")) #send names command to IRC server 
  
  userlist = ircsock.recv(2048).decode("UTF-8")
  if userlist.find('NAMES') != -1:
    print("..........")
    
    #TODO
    #split from string 
    #save items in list
  
  
  
  print("------------------")
  print("userlist: " + userlist)
  
  #return random user (item in list)
  #
  
  return user



#slap a random user in the chat
def slapuser(msg, target=channel):
  
  usertoslap = randomuser()
  message = msg + usertoslap + " *****"

  try:
    ircsock.send(bytes("PRIVMSG "+ target +" :"+ message +"\n", "UTF-8"))
  except:
    print("ERROR: Could not slap user: " + usertoslap)




#read random line from file
def random_line(filename):
  try:
    lines = open(filename).read().splitlines()
  except IOError:
    print("ERROR: Could not read from file: " + filename)

  return random.choice(lines)



#call the other functions as necessary and process the info
def main():
  
  joinchan(channel) #join the channel

  #infinite loop to continually check for and receive new info from server. This ensures our connection stays open. 
  while 1:
    try:
      #receiving information from the IRC server
      ircmsg = ircsock.recv(2048).decode("UTF-8")
    except:
      print("ERROR: IRC server information problem!")
    
    #remove any line break characters from the string
    ircmsg = ircmsg.strip('\n\r')

    #debugging: print the received information 
    print(ircmsg)

    #check if the information we received was standard messages in the channel 
    if ircmsg.find("PRIVMSG") != -1:
      #get name of the person who sent the message. 
      #Messages come in from from IRC in the format of 
      #":[Nick]!~[hostname]@[IP Address] PRIVMSG [channel] :[message]”

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
            slapuser("***** SLAPPED: ")
          
          #check for a ‘code’ at the beginning of a message and parse it to do a complex task. 
          #".tell [target] [message]” 
          if message[:5].find('!tell') != -1:
            target = message.split(' ', 1)[1]  #split the command from the rest of the message.
            if target.find(' ') != -1: #split full message incl spaces
                message = target.split(' ', 1)[1]
                target = target.split(' ')[0]

            #wrong input
            else:
              #target to the name of the user who sent the message (parsed from above)
              target = name
              message = "Message format should be ‘!tell [target] [message]’"
            
            sendmsg(message, target)

          #to exit bot
          #if name.lower() == adminname.lower() and message.rstrip() == exitcode:
          #  sendmsg("oh...okay. :'(", channel)
          #  ircsock.send(bytes("QUIT \n", "UTF-8")) #quit command to IRC server 
          #  return

          #to exit bot
          if message.rstrip() == exitcode:
            sendmsg("Oh...Okay. :'(", channel)
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