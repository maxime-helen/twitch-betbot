from tornado import testing
import ConfigParser

import os
import sys
import asyncore
import time

sys.path.insert(0, '../src')
sys.path.insert(0, '../lib')

from mock.Socket import Socket
from lib.TwitchClient import TwitchClient
from src.Game import Game

cfg = ConfigParser.ConfigParser()
cfg.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'language.cfg'))

PORT = 1507
BOTNAME = "BetBot"
CHATNAME = "foo"
READBUFFER = 2048
LANGUAGE = "EN"
VERBOSE = True

def get_language_script (option):
    return cfg.get(LANGUAGE, option)

def get_command_status_msg (state):
    return "PRIVMSG foo :%s %s\r\n" % (get_language_script("status"), state)

def get_command_last_winner_msg (last_winner):
    return "PRIVMSG foo :%s %s\r\n" % (get_language_script("last_winner"), last_winner)

def get_command_final_winner_msg (winner):
    return "PRIVMSG foo :%s %s\r\n" % (get_language_script("final_winner"), winner)

def get_command_final_no_winner_msg ():
    return "PRIVMSG foo :%s\r\n" % (get_language_script("final_no_winner"))

COMMAND_START_BET = "PRIVMSG foo :%s\r\n" % (get_language_script("start_bet"))
COMMAND_STOP_BET = "PRIVMSG foo :%s\r\n" % (get_language_script("stop_bet"))
COMMAND_NO_LAST_WINNER = "PRIVMSG foo :%s\r\n" % (get_language_script("no_last_winner"))
COMMAND_CMD_BET = "PRIVMSG foo :Moderators commands : !startbet, !stopbet, !statusbet, !final <final top>, !lastwinner\r\n"

# Test ws connection with node-compeer
class GameTest(testing.AsyncTestCase):

    def __before(self, messageBuffer, onmessage):
        socket = Socket(messageBuffer, onmessage)
        self.client = TwitchClient(self.io_loop, socket, BOTNAME, CHATNAME, READBUFFER, VERBOSE)
        self.game = Game(self.client, get_language_script, ["foo"])

    def __timeout(self):
        self.io_loop.stop()
        raise ValueError('Test time is out!')

    def __add_timeout(self, timeout):
        self.io_loop.add_timeout(time.time() + timeout, self.__timeout)
        
    # Test !cmdbet
    def test_startbet(self):
        def onsend(msg):
            if self.open_flag:
                self.assertEqual(msg, COMMAND_CMD_BET)
                self.io_loop.stop()

        messageBuffer = [
            "End of /NAMES list\n",
            ":foo!foo@foo.tmi.twitch.tv PRIVMSG #hello_world :!cmdbet\r\n"
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
            self.assertEqual(msg['command'], "cmdbet")


        port = 1111
        oauthKey = 'dsaf6+9+987'
        self.client.connect(port, oauthKey)
        self.io_loop.start()
        
 
    # Test "top <bet>" format
    def test_bet_format(self):                

        messageBuffer = [
            "End of /NAMES list\n",
            ":foo!foo@foo.tmi.twitch.tv PRIVMSG #hello_world :!top 111\r\n"
        ]
        
        self.__add_timeout(1)
        self.__before(messageBuffer, lambda(a): None)
        
        self.open_flag = False

        @self.client.on("open")
        def onOpen():
            self.open_flag = True

        @self.client.on("message")
        def onMessage(msg):
            self.assertEqual(self.open_flag, True)
            self.assertEqual(msg['command'], "top")
            self.assertEqual(msg['message'], "111")
            self.io_loop.stop()

        port = 1111
        oauthKey = 'dsaf6+9+987'
        self.client.connect(port, oauthKey)
        self.io_loop.start()

    # Test "startbet" command
    def test_startbet(self):
        def onsend(msg):
            if self.open_flag:
                self.assertEqual(msg, COMMAND_START_BET)
                self.io_loop.stop()

        messageBuffer = [
            "End of /NAMES list\n",
            ":foo!foo@foo.tmi.twitch.tv PRIVMSG #hello_world :!startbet\r\n"
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
            self.assertEqual(msg['command'], "startbet")


        port = 1111
        oauthKey = 'dsaf6+9+987'
        self.client.connect(port, oauthKey)
        self.io_loop.start()

    # Test regular game experience
    def test_regular_game_experience(self):
        self.index_top_saved = 0
        self.index_onsend = 0
        
        def check_fisrt_top_saved(username, bet):
            def callback() :
                user = self.game.get_username_by_first_bet(bet)
                self.assertEqual(username, user)
            return callback
        
        def check_state(state):
            def callback() :
                self.assertEqual(self.game.get_state(), state)
            return callback
        
        def check_final(username):
            def callback() :
                self.assertEqual(self.game.get_state(), 'init')
                self.assertEqual(self.game.get_winner(), username)
            return callback

        def empty_callback():
            def callback():
                pass
            return callback
        
        self.callbacks_on_message = [
            empty_callback(),
            empty_callback(),
            check_state('lobby'),
            empty_callback(),
            check_fisrt_top_saved("foo", 123),
            check_fisrt_top_saved("foo", 11),
            check_fisrt_top_saved("foo", 11),
            check_state('game'),
            empty_callback(),
            check_final("foo"),
            empty_callback(),
            empty_callback()
        ]
        
        
        def check_onsend_message(cmd_msg):
            def callback(msg) :
                self.assertEqual(msg, cmd_msg)
            return callback

        self.callbacks_onsend = [
            check_onsend_message(COMMAND_NO_LAST_WINNER),
            check_onsend_message(get_command_status_msg('init')),
            check_onsend_message(COMMAND_START_BET),
            check_onsend_message(get_command_status_msg('lobby')),
            check_onsend_message(COMMAND_STOP_BET),
            check_onsend_message(get_command_status_msg('game')),
            check_onsend_message(get_command_final_winner_msg('foo')),
            check_onsend_message(get_command_last_winner_msg('foo')),
            check_onsend_message(get_command_status_msg('init'))
        ]
        
        def onsend(msg):
            if self.open_flag:
                self.callbacks_onsend[self.index_onsend](msg)
                self.index_onsend = self.index_onsend + 1
                if self.index_onsend == len(self.callbacks_onsend):
                    self.io_loop.stop()

        messageBuffer = [
            "End of /NAMES list\n",
            ":foo!foo@foo.tmi.twitch.tv PRIVMSG #hello_world :!lastwinner\r\n",
            ":foo!foo@foo.tmi.twitch.tv PRIVMSG #hello_world :!statusbet\r\n",
            ":foo!foo@foo.tmi.twitch.tv PRIVMSG #hello_world :!startbet\r\n",
            ":foo!foo@foo.tmi.twitch.tv PRIVMSG #hello_world :!statusbet\r\n",
            ":foo!foo@foo.tmi.twitch.tv PRIVMSG #hello_world :!top 123\r\n",
            ":foo!foo@foo.tmi.twitch.tv PRIVMSG #hello_world :!top 11\r\n",
            ":bar!bar@bar.tmi.twitch.tv PRIVMSG #hello_world :!top 11\r\n",
            ":foo!foo@foo.tmi.twitch.tv PRIVMSG #hello_world :!stopbet\r\n",
            ":foo!foo@foo.tmi.twitch.tv PRIVMSG #hello_world :!statusbet\r\n",
            ":foo!foo@foo.tmi.twitch.tv PRIVMSG #hello_world :!final 11\r\n",
            ":foo!foo@foo.tmi.twitch.tv PRIVMSG #hello_world :!lastwinner\r\n",
            ":foo!foo@foo.tmi.twitch.tv PRIVMSG #hello_world :!statusbet\r\n"
        ]
        
               
        self.__add_timeout(2)
        self.__before(messageBuffer, onsend)
        
        self.open_flag = False

        @self.client.on("open")
        def onOpen():
            self.open_flag = True

        @self.client.on("message")
        def onMessage(msg):
            self.assertEqual(self.open_flag, True)
            self.callbacks_on_message[self.index_top_saved]()
            self.index_top_saved = self.index_top_saved + 1

        port = 1111
        oauthKey = 'dsaf6+9+987'
        self.client.connect(port, oauthKey)
        self.io_loop.start()

    
    
if __name__ == '__main__':
    import unittest
    unittest.main()
