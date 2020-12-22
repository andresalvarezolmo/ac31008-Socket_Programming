#!/usr/bin/python3
import socket
import random
import argparse

#the socket to connect and communicate with the IRC server.
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #to connect using ipv4 server
# ircsock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM) #to connect using ipv6 server

#name of the server and channel we’ll be connecting to
server = "127.0.0.1" # Server localhost ipv4
# server = "::1" # Server localhost ipv6
# server = "fc00:1337::19" # Actual ipv6 Server that will be used for marking
port = 6667
channel = "#testing"

botnick = "BOT1" 
exitcode = "Bye " + botnick 
afile = 'facts.txt' #file saving the random facts available
users = [] #list with all users on the channel


# command line arguments
parser = argparse.ArgumentParser(description='IRC bot parameters.')
parser.add_argument("--hostname", "--h", help="enter the IP address of the server", required = False, default = server)
parser.add_argument("--portnumber", "--p", type=int, help="enter the port of the server", required = False, default = port)
parser.add_argument("--channelname", "--c", help="enter the name of the channel", required = False, default = channel)
parser.add_argument("--botname", "--b", help="enter the name of the bot", required = False, default = botnick)

args = parser.parse_args()
server = args.hostname
port = args.portnumber
channel = args.channelname
botnick = args.botname



#check replies from server for errors
def errors(message):
  errorcode = message.split(' ')[1] 
  print("*********")
  print("Error " + errorcode)
  
  if errorcode == '401':
    print("ERROR 401: No such nickname in channel!")
    quit()
  elif errorcode == '402':
    print("ERROR 402: No such server")
    quit()
  elif errorcode == '403':
    print("ERROR 403: No such channel")
    quit()
  elif errorcode == '404':
    print("ERROR 404: Cannot send to channel")
    quit()
  elif errorcode == '422':
    print("ERROR 424: File error")
    quit()
  elif errorcode == '433':
    print("ERROR 433: Botname '" + botnick + "' already in use! ")
    quit()
  else:
    return



#connect to server
def connect():
  global ircsock
  try:
    ircsock.connect((server, port)) # connect to server at port...
  except:
    print("ERROR: Could not connect to server: " + server)
    quit()

  try:
    #send some information to let the server know who we are. 
    ircsock.send(bytes("USER "+ botnick +" "+ botnick +" "+ botnick + " " + botnick + "\r\n", "UTF-8")) # user information
    ircsock.send(bytes("NICK "+ botnick +"\r\n", "UTF-8")) # assign the nick to the bot
    message = ircsock.recv(2048).decode("UTF-8")
    errors(message)
    print("here")
  except:
    print("ERROR: Could not send to server: " + server)
    quit()



# function to join a channel, pass name 
def joinchan(chan):
  #send the message to IRC as UTF-8 encoded bytes
  try:
    ircsock.send(bytes("JOIN "+ chan +"\r\n", "UTF-8")) 
  except:
    print("ERROR: Could not join channel: " + chan)
    quit()
  
  

#respond with "PONG :pingis" to any PING 
def pong():
  try:
    ircsock.send(bytes("PONG :pingis\r\n", "UTF-8"))
  except:
    print("ERROR: Could not send pong!")
    quit()
  else:
    print("PONG")



#send message to target 
def sendmsg(msg, target):
  try:
    ircsock.send(bytes("PRIVMSG "+ target +" :"+ msg +"\r\n", "UTF-8"))
  except:
    print("ERROR 404: Could not send message to: " + target)
    quit()



#function to update the list with users on the channel
def updateusers():
  try:
    ircsock.send(bytes("NAMES " + channel + "\r\n", "UTF-8")) #send names command to IRC server   
    userlist = ircsock.recv(2048).decode("UTF-8")
  except:
    print("ERROR: No connection to server found")
    quit()
  
  if userlist.find('NAMES') != -1:    
    #split usernames from string
    usernames = userlist.split(' :',1)[1].split('\n', 1)[0]
    global users 
    users = usernames.split(' ')
    print("\n__________USERS_____________")
    print(*users, sep = "\n")
    print("____________________________\n")



#return a random user on the channel
def randomuser():
  global users
  randuser = random.choice(users)
  return randuser
  
  

#slap a random user in the chat
def slapuser(target=channel):
  usertoslap = randomuser()
  message = "***** " + usertoslap + " WAS SLAPPED BY A TROUT *****"

  try:
    ircsock.send(bytes("PRIVMSG "+ target +" :"+ message +"\n", "UTF-8"))
  except:
    print("ERROR: Could not slap user: " + usertoslap)
    quit()



#read random line from file
def random_line(filename):
  try:
    lines = open(filename).read().splitlines()
  except IOError:
    print("ERROR: Could not read from file: " + filename)
    quit()

  return random.choice(lines)



#terminate the session 
def exit():
  sendmsg("Oh...Okay. :'(", channel)
  try:
    ircsock.send(bytes("QUIT \n", "UTF-8")) #quit command to IRC server
  except:
    print("ERROR: Could not send QUIT command")
    quit()



#call the other functions as necessary and process the info
def main():
  
  connect()
  joinchan(channel)

  import time
  #continually check for and receive new info from server
  while 1:
    time.sleep(1)
    try:
      ircmsg = ircsock.recv(2048).decode("UTF-8")
    except Exception as e:
      print("ERROR: IRC server problem! {}".format(e))
      quit()
    
    ircmsg = ircmsg.strip('\n\r')
    print(ircmsg)

    #check if the information we received was standard messages in the channel 
    if ircmsg.find("PRIVMSG") != -1:
     
      #IRC in the format of ":[Nick]!~[hostname]@[IP Address] PRIVMSG [channel] :[message]”
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

          #check for reqeust for slap
          if message.find('!slap') != -1:
            slapuser()
          
          #mesage "!tell [target] [message]” 
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
          if message.rstrip() == exitcode:
            exit()
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
        pong()

    updateusers()


#start program
main()