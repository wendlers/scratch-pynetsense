##
# This file is part of the uSherpa Python Library project
#
# Copyright (C) 2012 Stefan Wendler <sw@kaltpost.de>
#
# The uSherpa Python  Library is free software; you can redistribute 
# it and/or modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
#  version 2.1 of the License, or (at your option) any later version.
#
#  uSherpa Python Library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
# 
#  You should have received a copy of the GNU Lesser General Public
#  License along with the JSherpa firmware; if not, write to the Free
#  Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
#  02111-1307 USA.  
##

'''
This file provides the main API class for using uSherpa. 
'''

import threading
import struct
import SocketServer

HOST = "localhost"		# hostname/IP on which to listen for client connections
PORT = 42001			# port on which to listen for client connections 

class RemoteSonsorServerRequestHandler(SocketServer.BaseRequestHandler):
	'''
	TCP request handler. Note: only accepts one client connection at a time.
	'''

	sock = None

	def handle(self):
		'''
		Handle client connection.
		'''

		RemoteSonsorServerRequestHandler.sock = self.request

		while True:
			data = self.request.recv(4)

			if not data:
				print("\nClient closed connection")
				break

			(l, ) = struct.unpack('!I', data)
			
			data = self.request.recv(l)

			print("\nReceived message of lenght %d from %s: %s" % (l, self.client_address[0], data))
	
class SimpleShell:
	'''
	Simple shell for sending test messages to sensor clients.
	'''

	def showHelp(self):
		'''
		Show usage information (/q command)
		'''
	
		print("\n\nControll commands:")
		print("  /q  - quit server")
		print("  /h  - show this help")
		print("\nEverything elese will be send as is to client. Examples:")
		print("  sensor-update \"var\" 42")
		print("  broadcast \"msg\"\n")

	def start(self):
		'''
		Start shell main loop.
		'''

		print("\n*** Scratch remote sensor server mock. Use /h for help, /q to quit ***\n")

		while True:

			cmd = raw_input("> ")

			if cmd.lower() == '/q':
				break
			elif cmd.lower() == '/h':
				self.showHelp()
			elif len(cmd) > 0:
				print("Sending: %s" % cmd)
				RemoteSonsorServerRequestHandler.sock.sendall(struct.pack('!I', len(cmd)))
				RemoteSonsorServerRequestHandler.sock.sendall(cmd)	

try:

	server = SocketServer.TCPServer((HOST, PORT), RemoteSonsorServerRequestHandler)

	shell = SimpleShell()

	server_thread = threading.Thread(target=server.serve_forever)

	server_thread.daemon = True
	server_thread.start()

	shell.start()
	server.shutdown()

except Exception as e:
	print(e)

