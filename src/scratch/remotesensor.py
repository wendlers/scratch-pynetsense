##
# This file is part of the Scratch Remote Sensor (SRS) Library project
#
# Copyright (C) 2012 Stefan Wendler <sw@kaltpost.de>
#
# The SRS Library is free software; you can redistribute 
# it and/or modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
#  version 2.1 of the License, or (at your option) any later version.
#
#  SRS Library is distributed in the hope that it will be useful,
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
This file is part of the Scratch Remote Sensor Library project
'''

import struct
import socket
import sys
import threading
import thread
import logging

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 42001

class SensorValues:
	'''
	Value holder class for remote sensor values. Every time a new value is assigned to a
	variable, a remote sensor update is sent to the server (via network).
	'''
	
	sensorClient = None

	def __init__(self, sensorClient):
		self.__setInternal("sensorClient", sensorClient)

	def __setInternal(self, name, value):
		self.__dict__[name] = value

	def __setattr__(self, name, value):
		self.set(name, value)

	def set(self, name, value, updateRemote = True):
		self.__setInternal(name, value)

		if updateRemote:
			self.sensorClient.sendMsg('sensor-update', varName=name, varValue=value)
		
	def get(self, name):
		return self.__dict__[name] 

class RemoteSensor(threading.Thread):
	'''
	Implementation of the Scratch Remote Sensor protocol.
	'''

	__sock = None
	values = None

	updateHandler  = None
	messageHandler = None

	def __init__(self, host = DEFAULT_HOST, port = DEFAULT_PORT):

		logging.info("Connection to %s:%d" % (host, port))

		RemoteSensor.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		RemoteSensor.__sock.connect((host, port))

		threading.Thread.__init__(self)
		self.daemon = True

		self.values = SensorValues(self)

	def __del__(self):

		try:
			RemoteSensor.__sock.close()
		except:
			pass

	def sendMsg(self, msgType, message = None, varName=None, varValue=None, **msgParam):

		msg = msgType

		if message == None and (varName == None or varValue == None):

			for k in msgParam.keys():

				msg = msg + ' "' + k + '" '

				if isinstance(msgParam[k], (int, long)):
					msg = msg + "%d" % msgParam[k] 
				elif isinstance(msgParam[k], (float)):
					msg = msg + "%f" % msgParam[k] 
				else:
					msg = msg + '"' +  msgParam[k] + '"'

		elif not varName == None and not varValue == None:

			msg = msg + ' "' + varName + '" '

			if isinstance(varValue, (int, long)):
				msg = msg + "%d" % varValue 
			elif isinstance(varValue, (float)):
				msg = msg + "%f" % varValue 
			else:
				msg = msg + '"' +  varValue + '"'

		else:

			msg = msg + ' "' + message + '"'

		logging.debug("Sending message: %s" % msg)

		RemoteSensor.__sock.sendall(struct.pack('!I', len(msg)))
		RemoteSensor.__sock.sendall(msg)

	def recvMsg(self):

		msg = RemoteSensor.__sock.recv(4)

		if not msg:
			return None

		(l, ) = struct.unpack('!I', msg)
				
		msg = RemoteSensor.__sock.recv(l)

		if not msg:
			return None

		return msg 

	def parseMsg(self, msg):
	
			logging.debug("Incoming message: %s" % msg)

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
 
				logging.debug("Element: %s" % se)

			logging.debug("Message-Type: %s" % mtype)

			if mtype == 'sensor-update':

				for k in melem.keys():
					logging.debug("Setting var %s to %s" % (k, melem[k]))
					self.values.set(k, melem[k], False)

					if not self.updateHandler == None:
						try:
							thread.start_new_thread(self.updateHandler, (k, melem[k]))
						except:
							pass

			elif mtype == 'broadcast':
				logging.debug("Message: %s" % mkey)

				if not self.messageHandler == None:
					try:
						thread.start_new_thread(self.messageHandler, (mtype, mkey))
					except:
						pass

			else:
				logging.warn("Unsupported message type: %s" % mtype)

	def bcastMsg(self, msg):

		self.sendMsg('broadcast', msg)

	def run(self):

		while True:

			msg = self.recvMsg()
	
			if not msg:
				break

			self.parseMsg(msg)
