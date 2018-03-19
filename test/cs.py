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
from src.Cs import Cs

cfg = ConfigParser.ConfigParser()
cfg.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'language.cfg'))

HOST = "0.0.0.0" 
PORT = 1507
BOTNAME = "battleroyale-test"
CHATNAME = "foo"
READBUFFER = 2048
LANGUAGE = "EN"
GAME = "CSGO"

VERBOSE = True
def get_language_script (game, option):
    return cfg.get("%s-%s"%(game, LANGUAGE), option)

COMMAND_SENT_MESSAGE2 = "PRIVMSG foo :%s\r\n" % (get_language_script(GAME, "start_bet"))
COMMAND_SENT_MESSAGE3 = "PRIVMSG foo :%s\r\n" % (get_language_script(GAME, "stop_bet"))
COMMAND_SENT_MESSAGE4 = "PRIVMSG foo :tefa %s\r\n"  % (get_language_script(GAME, "final_winner"))

def get_command_status_msg (state):
    return "PRIVMSG foo :%s %s\r\n" % (get_language_script(GAME, "status"), state)

def get_command_last_winner_msg (last_winner):
    return "PRIVMSG foo :%s %s\r\n" % (get_language_script(GAME, "last_winner"), last_winner)

def get_command_final_winner_msg (winner):
    return "PRIVMSG foo :%s %s\r\n" % (get_language_script(GAME, "final_winner"), winner)

def get_command_final_no_winner_msg ():
    return "PRIVMSG foo :%s\r\n" % (get_language_script(GAME, "final_no_winner"))

COMMAND_START_BET = "PRIVMSG foo :%s\r\n" % (get_language_script(GAME, "start_bet"))
COMMAND_STOP_BET = "PRIVMSG foo :%s\r\n" % (get_language_script(GAME, "stop_bet"))
COMMAND_NO_LAST_WINNER = "PRIVMSG foo :%s\r\n" % (get_language_script(GAME, "no_last_winner"))
COMMAND_CMD_BET = "PRIVMSG foo :Moderators commands : !startbet, !stopbet, !statusbet, !winner|loser, !lastwinner\r\n"

# Test ws connection with node-compeer
class CsTest(testing.AsyncTestCase):

    def __before(self, messageBuffer, onmessage):
        socket = Socket(messageBuffer, onmessage)
        self.client = TwitchClient(self.io_loop, socket, BOTNAME, CHATNAME, READBUFFER, VERBOSE)
        self.game = Cs(self.client, get_language_script, ["gr33nplant"])

    def __timeout(self):
        self.io_loop.stop()
        raise ValueError('Test time is out!')

    def __add_timeout(self, timeout):
        self.io_loop.add_timeout(time.time() + timeout, self.__timeout)
         
    # Test "top <bet>" format
    def test_bet_format(self):                

        messageBuffer = [
            "End of /NAMES list\n",
            ":gr33nplant!gr33nplant@gr33nplant.tmi.twitch.tv PRIVMSG #toytoy_ :!win 16-8\r\n"
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
            self.assertEqual(msg['command'], "win")
            self.assertEqual(msg['message'], "16-8")
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
            ":gr33nplant!gr33nplant@gr33nplant.tmi.twitch.tv PRIVMSG #toytoy_ :!startbet\r\n"
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
        
        def check_top_saved(username, bet, score):
            def callback() :
                user = self.game.get_first_username_by_bet(bet, score)
                print user
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
            check_top_saved("gr33nplant", "win", "16-3"),
            check_top_saved("gr33nplant", "win", "3-16"),
            check_top_saved("tefa", "lose", "12-16"),
            check_state('game'),
            empty_callback(),
            check_final("tefa"),
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
            check_onsend_message(get_command_final_winner_msg('tefa')),
            check_onsend_message(get_command_last_winner_msg('tefa')),
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
            ":gr33nplant!gr33nplant@gr33nplant.tmi.twitch.tv PRIVMSG #toytoy_ :!lastwinner\r\n",
            ":gr33nplant!gr33nplant@gr33nplant.tmi.twitch.tv PRIVMSG #toytoy_ :!statusbet\r\n",
            ":gr33nplant!gr33nplant@gr33nplant.tmi.twitch.tv PRIVMSG #toytoy_ :!startbet\r\n",
            ":gr33nplant!gr33nplant@gr33nplant.tmi.twitch.tv PRIVMSG #toytoy_ :!statusbet\r\n",
            ":gr33nplant!gr33nplant@gr33nplant.tmi.twitch.tv PRIVMSG #toytoy_ :!win 16-3\r\n",
            ":gr33nplant!gr33nplant@gr33nplant.tmi.twitch.tv PRIVMSG #toytoy_ :!win 12-16\r\n",
            ":tefa!tefa@tefa.tmi.twitch.tv PRIVMSG #toytoy_ :!lose 12-16\r\n",
            ":gr33nplant!gr33nplant@gr33nplant.tmi.twitch.tv PRIVMSG #toytoy_ :!stopbet\r\n",
            ":gr33nplant!gr33nplant@gr33nplant.tmi.twitch.tv PRIVMSG #toytoy_ :!statusbet\r\n",
            ":gr33nplant!gr33nplant@gr33nplant.tmi.twitch.tv PRIVMSG #toytoy_ :!loser 16-12\r\n",
            ":gr33nplant!gr33nplant@gr33nplant.tmi.twitch.tv PRIVMSG #toytoy_ :!lastwinner\r\n",
            ":gr33nplant!gr33nplant@gr33nplant.tmi.twitch.tv PRIVMSG #toytoy_ :!statusbet\r\n"
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
