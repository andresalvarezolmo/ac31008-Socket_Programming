#!/usr/bin/python3
import socket
import random
import argparse

ircsock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
server = "::1"
# server = "fc00:1337::19" # Actual ipv6 Server that will be used for marking
port = 6667
channel = "#testing"

botnick = "BOT" 
exitcode = "Bye " + botnick 
afile = 'facts.txt' #file saving the random facts available
users = [] #list with all users on the channel

parser = argparse.ArgumentParser(description='IRC bot parameters.')
parser.add_argument("-h", "--hostname", help="enter the IP address of the server", required = False, default = server)
parser.add_argument("-p", "--port", type=int, help="enter the port of the server", required = False, default = port)
parser.add_argument("-c", "--channelname", help="enter the name of the channel", required = False, default = channel)
parser.add_argument("-b", "--botname", help="enter the name of the bot", required = False, default = botnick)

args = parser.parse_args()
server = args.hostname
port = args.portnumber
channel = args.channelname
botnick = args.botname


try:
  ircsock.connect((server, port))
except:
  print("ERROR: Could not connect to server: " + server)
  quit()

try:
  # send some information to let the server know who we are.
  ircsock.send(bytes("USER "+ botnick +" "+ botnick +" "+ botnick + " " + botnick + "\r\n", "UTF-8"))
  ircsock.send(bytes("NICK "+ botnick +"\r\n", "UTF-8"))
except:
  print("ERROR: Could not send to server: " + server)
  quit()


def joinchan(chan):
  """
  function to join a channel, pass name
  :param chan: channel to be joined
  :return:
  """
  try:
    ircsock.send(bytes("JOIN "+ chan +"\r\n", "UTF-8")) 
  except:
    print("ERROR: Could not join channel: " + chan)
    quit()

def pong():
  """
  respond with "PONG :pingis" to any PING
  """
  try:
    ircsock.send(bytes("PONG :pingis\r\n", "UTF-8"))
  except:
    print("ERROR: Could not send pong!")
    quit()
  else:
    print("PONG")



def sendmsg(msg, target):
  """
  send message to target
  :param msg: the message that should be send
  :param target: the target, either a nick or channel name
  """
  try:
    ircsock.send(bytes("PRIVMSG "+ target +" :"+ msg +"\r\n", "UTF-8"))
  except:
    print("ERROR 404: Could not send message to: " + target)
    quit()

def updateusers():
  """
  function to update the list with users on the channel
  """
  ircsock.send(bytes("NAMES " + channel + "\r\n", "UTF-8")) #send names command to IRC server   
  
  try:
    userlist = ircsock.recv(2048).decode("UTF-8")
  except:
    print("ERROR: ")
    quit()
  
  if userlist.find('NAMES') != -1:
    usernames = userlist.split(' :',1)[1].split('\n', 1)[0]
    global users 
    users = usernames.split(' ')
    print("\n__________USERS_____________")
    print(*users, sep = "\n")
    print("____________________________\n")

def randomuser():
  """
  #return a random user on the channel
  :return: a random user
  """
  global users
  randuser = random.choice(users)
  return randuser

def slapuser(target=channel):
  """
  slap a random user in the chat
  :param target: the channel in which the user should be slapped
  :return:
  """
  usertoslap = randomuser()
  message = "***** " + usertoslap + " WAS SLAPPED BY A TROUT *****"

  try:
    ircsock.send(bytes("PRIVMSG "+ target +" :"+ message +"\r\n", "UTF-8"))
  except:
    print("ERROR: Could not slap user: " + usertoslap)
    quit()

def random_line(filename):
  """
  read a random fact from the factsfile.
  :param filename: the factsfile
  :return: a random fact from the facts file
  """
  try:
    lines = open(filename).read().splitlines()
  except IOError:
    print("ERROR 424: Could not read from file: " + filename)
    quit()

  return random.choice(lines)



def erromessage():
  """
  print an error
  """
  print("error")

def main():
  """
  call the other functions as necessary and process the info
  """
  
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
            sendmsg("Oh...Okay. :'(", channel)
            ircsock.send(bytes("QUIT \n", "UTF-8"))
            return

        #if message from private channel
        if origin.lower() == botnick.lower():
           
          #send fact after every message
          if message != -1:
            fact = random_line(afile)
            sendmsg(fact, name)

    else:
      if ircmsg.find("PING :") != -1:
        pong()

    updateusers()


if __name__ == "__main__":
  main()