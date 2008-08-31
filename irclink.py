#!/usr/bin/python
# -*- coding: utf-8 -*-
"""                             
Irc Link 1.0
	by Sunny Ripert <negatif+AT+gmail+DOT+com>
 
What ?
	Provides a sort of a Stargate between different IRC channels and servers
	by repeating the messages it receives on all the other channels.
 
License
	This program is free software; you can redistribute it and/or modify it under
	the terms of the GNU General Public License as published by the Free Software
	Foundation; either version 2 of the License, or (at your option) any later 
	version.
 
	This program is distributed in the hope that it will be useful, but WITHOUT 
	ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
	FOR A PARTICULAR PURPOSE. See the GNU General Public License for more 
	details.
 
	You should have received a copy of the GNU General Public License along with
	this program; if not, write to the Free Software Foundation, Inc., 675 Mass 
	Ave, Cambridge, MA 02139, USA.
"""
import socket
 
class Server:
	"""IRC Server connection, needs the socket library"""
	def __init__(self, name, host, port, nick, ident, realname, channels):
		"""Initialises the socket connecting to an IRC server"""
		self.name = name
		self.channels = channels
		self.host = host
		self.port = port
		self.nick = nick
		self.ident = ident
		self.realname = realname
		self.socket = socket.socket()
		self.socketbuffer = ""
 
	def connect(self):
		"""Connects to the socket and sets default socket options"""
		self.socket.connect((self.host, self.port))
		self.socket.settimeout(2.0)
		self.send("NICK %s" % self.nick)
		self.send("USER %s %s bla :%s" % (self.ident, self.host, self.realname))
 
	def disconnect(self, message = ""):
		"""Kindly quits the IRC server with a message"""
		self.send("QUIT :" + message)
 
	def send(self, command):
		"""Send line to socket"""
		print "%s --> %s" % (self.name, command)
		self.socket.send(command + "\r\n")
 
	def message(self, who, message):
		"""Send a private message to a person or a public message on a channel"""
		self.send("PRIVMSG %s :%s" % (who, message))
 
	def getmessages(self):
		"""Gets the last lines from the buffer, waiting for the timeout, pongs back
			if necessary, joins channels on motd end and returns tuple containing
			string channel, string messagesender, string message"""
 
		try:
			self.socketbuffer += self.socket.recv(1024)
		except socket.timeout:
			return []
 
		bufferlines = self.socketbuffer.split("\n")
		self.socketbuffer = bufferlines.pop()
		messages = []
 
		for line in bufferlines:
			print "%s <-- %s" % (s.name, line)
			words = line.rstrip().split()
 
			if words[0] == "PING": # ping
				self.send("PONG " + words[1])
			elif words[1] == "376": # end of MOTD
				self.send("JOIN " + ",".join(self.channels))
			elif words[1] == "PRIVMSG":
				channel = words[2]
				who = words[0][1:].split('!')[0] # message sender
				message = ' '.join([words[3][1:]] + words[4:]).strip() # strips ':' and whitespace
				if who != self.nick and message and (channel in self.channels): # channel message
					messages.append((channel, who, message)) # returns only other people's
 
		return messages
 
 
 
 
 
# options
servers = [
	Server("fnode", "irc.freenode.org", 6667, "escalink", "escalink", "Escalope netlink bot", ['#escalope']),
	Server("idev",  "irc.idevelop.org", 6667, "escalink", "escalink", "Escalope netlink bot", ['#escalope']),
]
# end of options
 
 
 
for s in servers:
	s.connect()
 
try:
	online = True
	while online:
		for s in servers:
			for channel, who, message in s.getmessages():
				for outerserv in servers:
					for outerchan in outerserv.channels:
						if (s.name, channel) != (outerserv.name, outerchan):
							outerserv.message(channel, "@%s <%s> %s" % (s.name, who, message))
 
except KeyboardInterrupt:
	print "Quitting..."
 
for s in servers:
	s.disconnect()

