import threading
import struct
import SocketServer

class RemoteSonsorServerRequestHandler(SocketServer.BaseRequestHandler):

	sock = None

	def handle(self):

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

	def __init__(self):
		pass

	def showHelp(self):
	
		print("\n\nControll commands:")
		print("  /q  - quit server")
		print("  /h  - show this help")
		print("\nEverything elese will be send as is to client. Examples:")
		print("  sensor-update \"var\" 42")
		print("  broadcast \"msg\"\n")

	def start(self):

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

	HOST, PORT = "localhost", 42001 

	server = SocketServer.TCPServer((HOST, PORT), RemoteSonsorServerRequestHandler)

	shell = SimpleShell()

	server_thread = threading.Thread(target=server.serve_forever)

	server_thread.daemon = True
	server_thread.start()

	shell.start()
	server.shutdown()

except Exception as e:
	print(e)

