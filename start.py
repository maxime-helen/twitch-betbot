import sys
import signal
import socket
import ConfigParser
from tornado import ioloop

from lib.TwitchClient import TwitchClient
from src.Battleroyale import Battleroyale

io_loop = ioloop.IOLoop.current()

def do_stop(signum, frame):
    ioloop.IOLoop.current().stop()

def sig_exit(signum, frame):
    ioloop.IOLoop.current().add_callback_from_signal(do_stop)

signal.signal(signal.SIGINT, sig_exit)
signal.signal(signal.SIGINT, sig_exit)

cfg = ConfigParser.ConfigParser()
cfg.read('config.cfg')

botName = 'BetBot'
chatName = cfg.get('profil', 'channel')
language = cfg.get('profil', 'language')
mods_list = cfg.get('profil', 'mods_list').split(',')

port = 6667
readBuffer = cfg.getint('bot', 'readBuffer')
oauthKey = cfg.get('bot', 'oauthKey')
verbose = cfg.getboolean('bot', 'verbose')

cfg = ConfigParser.ConfigParser()
cfg.read('language.cfg')

def get_language_script (game, option):
    return cfg.get("%s-%s" % (game, language), option)

client = TwitchClient(ioloop, socket, botName, chatName, readBuffer, verbose)
Battleroyale(client, get_language_script, mods_list)
@client.on("open")
def onOpen():
    print "%s bot is connected to %s chat" % (botName, chatName)
client.connect(port, oauthKey)
io_loop.start()
