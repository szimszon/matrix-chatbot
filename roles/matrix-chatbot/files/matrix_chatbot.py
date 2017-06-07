#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import re
import logging
import getpass
import datetime
import time
import subprocess
from optparse import OptionParser
import os

from matrix_client.client import MatrixClient

if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input


class ChatBot(object):

    def __init__(self, opts):
        jid=opts.jid
        password=opts.password
        url=opts.url
        room_id_alias=opts.room
        
        #
        # Connect to the server
        # ######################
        self.client=MatrixClient(url)
        try:
          self.token=self.client.login_with_password(username=jid, password=password)
        except MatrixRequestError as e:
          print(e)
          if e.code == 403:
            print("Bad username or password.")
            sys.exit(4)
          else:
            print("Check your sever details are correct.")
            sys.exit(2)
        except MissingSchema as e:
          print("Bad URL format.")
          print(e)
          sys.exit(3)        

        #
        # Connect to the room
        # ####################
        try:
            self.room = self.client.join_room(room_id_alias)
        except MatrixRequestError as e:
          print(e)
          if e.code == 400:
            print("Room ID/Alias in the wrong format")
            sys.exit(11)
          else:
            print("Couldn't find room.")
            sys.exit(12)

        self.room.send_text('I\'m now online.')
        self.opts=opts
        
        self.regexp=self.opts.regexp if self.opts.regexp else '^do:[ ]*(.*)::$'
        self.argsep=self.opts.argsep if self.opts.argsep else ';'
        self.inittalkbacktimeout=int(self.opts.inittalkbacktimeout) if self.opts.inittalkbacktimeout else 5
        self.talkbacktimeout=int(self.opts.talkbacktimeout) if self.opts.talkbacktimeout else 30

        #
        # Listen in the room
        # ##################
        self.room.add_listener(self.command)
        self.client.start_listener_thread()
        while True:
            try:
              time.sleep(5)
            except Exception,e:
              self.room.send_text('I\'m leaving now... ('+str(e)+")")

    def command(self,room,event):
      
      #
      # Check if the request is authentic
      # ######################################################
      if event['type'] != "m.room.message" or event['content']['msgtype'] != "m.text":
        return True
      if str(event['sender']) == str(self.opts.jid):
        return True
      if str(event['sender']) != str(opts.boss):
        logging.info('Not a Boss is talking to us but ::'+event['sender']+'::')
        return True
      body=event['content']['body'].strip()
      cmd=re.compile(self.regexp).match(body)
      if not cmd:
        return True
      cmd=cmd.group(1).split(self.argsep)
      if '..' in cmd[0]:
        return True
      command=cmd[0]
      cmd[0]=os.path.join(self.opts.scriptdir,cmd[0])
      if not os.path.isfile(cmd[0]):
        return True

      #
      # Execute the script
      # ##################
      try:
        logging.info(str(opts.boss)+" asked us to do (("+str(cmd)+"))")
        w=datetime.datetime.now()+datetime.timedelta(seconds=self.inittalkbacktimeout)
        starttime=datetime.datetime.now()
        res=subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             close_fds=True,
                             bufsize=0,
                             )
        stdout="↶--------------- ["+str(command)+"] ("+str(datetime.datetime.now())+") ---------------↷\n"
        stderr=""
        #
        # Time to time put some feedback to the XMPP's chat
        # ##################################################
        while ( res.poll() == None ):
          time.sleep(1)
          stdout+=res.stdout.readline()
          if w<=datetime.datetime.now():
            if len(stdout)>0:
              self.room.send_text(str(stdout))
        
            w=datetime.datetime.now()+datetime.timedelta(seconds=self.talkbacktimeout)
            stdout=""

        (stdoutplus,stderrplus)=res.communicate()
        stdout+=stdoutplus
        stderr+=stderrplus

      except Exception,e:
        stderr="[%s]"%str(e)
        stdout=""
      #
      # Finally put the last messages to the chat
      # ##########################################
      if len(stderr)>0:
        stdout+="\n↓--------------- ["+str(command)+"] ---------------↓"
        stdout+="\n======= ERR =======\n"+str(stderr)+"\n======= ERR ======="
      self.room.send_text(str(stdout)+\
                                "\n↳--------------- ["+str(command)+\
                                "] {"+str(res.returncode)+"} ("+str(datetime.datetime.now())+\
                                ", "+str(datetime.datetime.now()-starttime)+") ---------------↲")
      return True




if __name__ == '__main__':
    # Setup the command line arguments.
    optp = OptionParser()

    # Output verbosity options.
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)
    
    # UID and password options.
    optp.add_option("-j", "--jid", dest="jid",
                    help="UID to use")
    optp.add_option("-p", "--password", dest="password",
                    help="password to use")
    optp.add_option("-b", "--boss", dest="boss",
                    help="The boss UID")
    optp.add_option("-u", "--url", dest="url",
                    help="Matrix server URL")
    optp.add_option("-o", "--room", dest="room",
                    help="Matrix room alias")

    
    # command execution
    optp.add_option("-s", "--scriptdir", dest="scriptdir",
                    help="directory of scripts",
                    default="/usr/local/lib/chatbot/")
    optp.add_option("-r", "--regexp", dest="regexp",
                    help="regexp to match the command",
                    default="^do:[ ]*(.*)::$")
    optp.add_option("-a", "--argsep", dest="argsep",
                    help="command argumentum separator",
                    default=";")

    # timeouts for talking the stdout back to jabber user
    optp.add_option("-i", "--init-talkback-timeout", dest="inittalkbacktimeout",
                    help="initial talkback timeout",
                    default=5)
    optp.add_option("-t", "--talkback-timeout", dest="talkbacktimeout",
                    help="talkback timeout",
                    default=30)

    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

    if opts.jid is None:
        opts.jid = raw_input("Username: ")
    if opts.password is None:
        opts.password = getpass.getpass("Password: ")
    if opts.url is None:
       opts.url = raw_input("Matrix server url: ")
    if opts.room is None:
       opts.room = raw_input("Matrix room alias: ")

    # Setup the ChatBot and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    bot = ChatBot(opts)
