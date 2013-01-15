import struct
import SocketServer

class TCPHandler(SocketServer.BaseRequestHandler):
	"""
	The RequestHandler class for our server.
	It is instantiated once per connection to the server, and must
	override the handle() method to implement communication to the
	client.
	"""

	def handle(self):

		while True:
			data = self.request.recv(4)

			if not data:
				print "Connection closed"
				break

			(l, ) = struct.unpack('!I', data)
			
			data = self.request.recv(l)

			print("Message of lenght %d received from %s: %s" % (l, self.client_address[0], data))

			# self.wfile.write(self.data.upper())

class TCPServer(SocketServer.TCPServer):
	pass
	
	"""
	def handle_error(self, request, client_address):
		print("Error on handle request from client: %s" % client_address)
	"""

if __name__ == "__main__":
	HOST, PORT = "localhost", 9999

	# Create the server, binding to localhost on port 9999
	server = TCPServer((HOST, PORT), TCPHandler)

	# Activate the server; this will keep running until you
	# interrupt the program with Ctrl-C
	server.serve_forever()
