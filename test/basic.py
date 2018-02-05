from tornado import testing

import sys
import asyncore
import time

sys.path.insert(0, '../src')
sys.path.insert(0, '../lib')

from mock.Socket import Socket
from lib.TwitchClient import TwitchClient
from src.Basic import Basic

def return_value_of_time(basic):
    return "PRIVMSG foo :It's %s UTC-5 in Toronto\r\n" % basic.get_time_test()

HOST = "0.0.0.0" 
PORT = 1507
BOTNAME = "battleroyale-test"
CHATNAME = "foo"
READBUFFER = 1024
COMMAND_SENT_MESSAGE = 'PRIVMSG foo :!bot, !cmd(s), !discord, !followage, !giveaway, !h1options, !snapchat, !steam, !time, !twitter, !uptime\r\n'
VERBOSE = True


# Test ws connection with node-compeer
class BasicTest(testing.AsyncTestCase):

    def __before(self, messageBuffer, onmessage):
        socket = Socket(messageBuffer, onmessage)
        self.client = TwitchClient(self.io_loop, socket, BOTNAME, CHATNAME, READBUFFER, VERBOSE)
        self.basic = Basic(self.client, None)

    def __timeout(self):
        self.io_loop.stop()
        raise ValueError('Test time is out!')

    def __add_timeout(self, timeout):
        self.io_loop.add_timeout(time.time() + timeout, self.__timeout)

    def test_command_cmd(self):
        def onsend(msg):
            if self.open_flag:
                self.assertEqual(msg, COMMAND_SENT_MESSAGE)
                self.io_loop.stop()

        messageBuffer = [
            "End of /NAMES list\n",
            ":gr33nplant!gr33nplant@gr33nplant.tmi.twitch.tv PRIVMSG #toytoy_ :!cmd\r\n"
        ]
        
        self.__add_timeout(1)
        self.__before(messageBuffer, onsend)
        
        self.open_flag = False

        @self.client.on("open")
        def onOpen():
            self.open_flag = True

        @self.client.on("message")
        def onMessage(msg):
            self.assertEqual(self.open_flag, True)
            self.assertEqual(msg['command'], "cmd")

        port = 1111
        oauthKey = 'dsaf6+9+987'
        self.client.connect(port, oauthKey)
        self.io_loop.start()
        
    def test_command_time(self):
        def onsend(msg):
            if self.open_flag:
                self.assertEqual(msg, return_value_of_time(self.basic))
                self.io_loop.stop()

        messageBuffer = [
            "End of /NAMES list\n",
            ":gr33nplant!gr33nplant@gr33nplant.tmi.twitch.tv PRIVMSG #toytoy_ :!time\r\n"
        ]
        
        self.__add_timeout(1)
        self.__before(messageBuffer, onsend)
        
        self.open_flag = False

        @self.client.on("open")
        def onOpen():
            self.open_flag = True

        @self.client.on("message")
        def onMessage(msg):
            self.assertEqual(self.open_flag, True)
            self.assertEqual(msg['command'], "time")

        port = 1111
        oauthKey = 'dsaf6+9+987'
        self.client.connect(port, oauthKey)
        self.io_loop.start()

if __name__ == '__main__':
    import unittest
    unittest.main()
