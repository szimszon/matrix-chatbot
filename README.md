# matrix-chatbot

This is a simple script to listen on a ![matrix server](http://matrix.org/) for messages from a specific account (*BOSS*) in a specific room and if the message matches a defined *REGEXP* (do:command::) it will execute a specific command.
Like:
```
  do:ls::
```
will execute the **ls** program placed in *SCRIPTDIR* (/usr/local/lib/chatbot/ls)

You can push arguments to this scripts with **;** *ARGSEP* like: 
```
do:command;arg1;arg2[;...]::
```
## help
<pre>
./matrix_chatbot.py --help
Usage: matrix_chatbot.py [options]

Options:
  -h, --help            show this help message and exit
  -q, --quiet           set logging to ERROR
  -d, --debug           set logging to DEBUG
  -v, --verbose         set logging to COMM
  -j JID, --jid=JID     UID to use
  -p PASSWORD, --password=PASSWORD
                        password to use
  -b BOSS, --boss=BOSS  The boss UID
  -u URL, --url=URL     Matrix server URL
  -o ROOM, --room=ROOM  Matrix room alias
  -s SCRIPTDIR, --scriptdir=SCRIPTDIR
                        directory of scripts
  -r REGEXP, --regexp=REGEXP
                        regexp to match the command
  -a ARGSEP, --argsep=ARGSEP
                        command argumentum separator
  -i INITTALKBACKTIMEOUT, --init-talkback-timeout=INITTALKBACKTIMEOUT
                        initial talkback timeout
  -t TALKBACKTIMEOUT, --talkback-timeout=TALKBACKTIMEOUT
                        talkback timeout
</pre>

## Requirements

- ![Matrix Client-Server SDK for Python 2 and 3](https://github.com/matrix-org/matrix-python-sdk/)
- you need to register a user for the bot on the matrix server
- start a direct chat from the *BOSS* user account to the bot, you will need the room's ID to set up the bot's config file

## Install

1. copy the roles/matrix-chatbot/files/matrix_chatbot.py into /usr/local/bin directory
1. copy the files from roles/matrix-chatbot/files/lib/ directory to /usr/local/lib/chatbot/ directory
1. set up the sudoers file for the chatbot user so the user can run the requested scripts and commands
1. for systemd systems copy the roles/matrix-chatbot/templates/matrix-chatbot.service.j2 file into /etc/systemd/system/matrix-chatbot.service directory
1. setup the matrix-chatbot.service file
1. systemctl daemon-reload
1. systemctl enable chatbot
1. systemctl start chatbot

## Ansible

In the roles directory you can find ansible roles for set up matrix chatbot...

