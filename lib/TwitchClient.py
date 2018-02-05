from pyee import EventEmitter
from tornado import ioloop

import string

twitchUrl = "irc.twitch.tv";
joinedRoomLogTrigger = "End of /NAMES list";

class TwitchClient (EventEmitter):
	
	def __init__(self, io_loop, socket, botName, chatName, readBuffer, verbose):
		EventEmitter.__init__(self)
		self.io_loop = io_loop
		self.socket = socket.socket()
		self.botName = botName
		self.chatName = chatName
		self.readBuffer = readBuffer
		self.verbose = verbose
	
	# below method is inspired from https://github.com/twitchdev/chat-samples/blob/master/javascript/chatbot.js#L99
	def __formatLine(self, line):
		parsedMessage = {
			"message": None,
			"tags": None,
			"command": None,
			"original": line,
			"channel": None,
			"username": None
		}

		if line[0] == ':' :
			startUserIndex = line.index('!') + 1
			endUserIndex = line.index('@')
			parsedMessage["username"] = line[startUserIndex:endUserIndex]

			startTagIndex = line.index(' ', endUserIndex + 1) + 1
			endTagIndex = line.index(' ', startTagIndex + 1)
			parsedMessage["tags"] = line[startTagIndex:endTagIndex]

			startChannelIndex = line.index(' ', endTagIndex)
			endChannelIndex = line.index(' ', startChannelIndex + 1)
			parsedMessage["channel"] = line[startChannelIndex:endChannelIndex]

			startMessageIndex = line.index(' :', endChannelIndex) + 2
			endMessageIndex = len(line)
			temp = line[startMessageIndex:endMessageIndex-1]
			if temp[0] == '!':
				endMessageIndex = len(temp)
				try :
					endCmdIndex = temp.index(" ")
					parsedMessage["command"] = temp[1:endCmdIndex]
					parsedMessage["message"] = temp[endCmdIndex + 1:endMessageIndex]
				except :
					parsedMessage["command"] = temp[1:endMessageIndex]
			else:
				parsedMessage["message"] = line[startMessageIndex:endMessageIndex]
		
		return parsedMessage

	def sendMessage(self, msg):
		msg = "PRIVMSG %s :%s\r\n" % (self.chatName, msg)
		self.socket.send(msg)
		print("Sent: " + msg)
		
	def print_log(self, log):
		if self.verbose :
			print log.translate(None, '\r\n')
			
	def connect(self, port, oauthKey):
		self.socket.connect((twitchUrl, port))

		self.socket.send("PASS oauth:%s \r\n" % (oauthKey))
		self.socket.send("NICK %s \r\n" % (self.botName))
		self.socket.send("JOIN %s \r\n" % (self.chatName))

		self.readbuffer = ""
		self.connected = False
		
		def parse_inbound_data():
			self.readbuffer = self.readbuffer + self.socket.recv(self.readBuffer)
			temp = string.split(self.readbuffer, "\n")
			self.readbuffer = temp.pop()
			for line in temp:
				self.print_log("Received: %s" % line)
				if not self.connected:
					if joinedRoomLogTrigger in line:
						self.emit("open")
						self.connected = True
				else:
					parsedMessage = self.__formatLine(line)
					self.print_log("Formatted: %s" % parsedMessage)
					self.emit("message", parsedMessage)
		
		ioloop.PeriodicCallback(parse_inbound_data, 100).start()
	