import struct
import socket
import sys
import threading

HOST, PORT = "localhost", 42001

class RemoteSensorClient(threading.Thread):

	sock = None

	def __init__(self, host, port):

		RemoteSensorClient.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		RemoteSensorClient.sock.connect((host, port))

		threading.Thread.__init__(self)
		self.daemon = True

	def __del__(self):

		try:
			RemoteSensorClient.sock.close()
		except:
			pass

	def sendMsg(self, msgType, message = None, **msgParam):

		msg = msgType

		if message == None:

			for k in msgParam.keys():

				msg = msg + ' "' + k + '" '

				if isinstance(msgParam[k], (int, long)):
					msg = msg + "%d" % msgParam[k] 
				elif isinstance(msgParam[k], (float)):
					msg = msg + "%f" % msgParam[k] 
				else:
					msg = msg + '"' +  msgParam[k] + '"'

		else:

			msg = msg + ' "' + message + '"'

		print("Constructed message: %s" % msg)

		RemoteSensorClient.sock.sendall(struct.pack('!I', len(msg)))
		RemoteSensorClient.sock.sendall(msg)

	def recvMsg(self):

		msg = RemoteSensorClient.sock.recv(4)

		if not msg:
			return None

		(l, ) = struct.unpack('!I', msg)
				
		msg = RemoteSensorClient.sock.recv(l)

		if not msg:
			return None

		return msg 


	def parseMsg(self, msg):
	
			print("Incoming message: %s" % msg)

			melemRaw = msg.split()
			melem = {} 
			mtype = None
			mkey  = None
			mval  = None

			for e in melemRaw:

				se = e.strip()

				if mtype == None:
					mtype = se.lower()	
				elif mkey == None:
					mkey = se[1:-1]
				else:
					try:	
						if se[0:1] == '"':
							mval = se[1:-1]
						elif '.' in se:
							mval = float(se)
						else:
							mval = int(se)
					except:
						mval = se

					melem[mkey] = mval
					mkey = None
					mval = None
 
				print("Element: %s" % se)

			print("Message-Type: %s" % mtype)

			if mtype == 'sensor-update':
				print("Message-Elem: %s" % melem)
			elif mtype == 'broadcast':
				print("Message: %s" % mkey)
			else:
				print("Unsupported message type")

	def run(self):

		while True:

			msg = self.recvMsg()
	
			if not msg:
				break

			self.parseMsg(msg)
	
try:
	rs = RemoteSensorClient(HOST, PORT)
	rs.start()
	
	rs.sendMsg('sensor-update', key1='Hello World 2013')
	rs.sendMsg('broadcast', 'foobar')

	raw_input('Press Enter to quit...')
	
except Exception as e:
	print(e)
