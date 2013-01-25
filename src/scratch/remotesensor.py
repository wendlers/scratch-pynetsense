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

Minimal Usage example:
----------------------

from scratch.remotesensor import RemoteSensor 

try:
	# Remote sensor connected to default host/port (localhost:42001)
	rs = RemoteSensor()
	rs.connect()

	# Start receiver thread
	rs.start()
	
	# Create new sensor variable 'a', set value to 1. This will result
    # in a 'sensor-update' message sent to Scratch sensor server. 
	rs.values.a = 1 

	# Create an other variable
	rs.values.b = 0.2 

	# An yet an other ...
	rs.values.x = "dynamic sensor-update"

	# Broadcast a message ...
	rs.bcastMsg('foobar')

	raw_input('Press Enter to quit...\n')
	
except Exception as e:
	print(e)

'''

import struct
import socket
import sys
import threading
import thread
import logging
import time

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 42001

class SensorValues:
	'''
	Value holder class for remote sensor values. Every time a new value is assigned to a
	variable, a remote sensor update is sent to the server (via network).

	This class is used inernally within the @RemoteSensor class.
	'''
	
	sensorClient = None

	def __init__(self, sensorClient):
		'''
		Construct a new sensor value holder.

		@param	sensorClient	reference to @RemoteSensor client instance	
		'''
		self.__setInternal("sensorClient", sensorClient)

	def __setInternal(self, name, value):
		'''
		Set value of named variable only in internal dictionary (don't send
		update message to sensor server).

		@param	name	name of variable to assign a value
		@param	value	value to be assigned
		'''
		self.__dict__[name] = value

	def __setattr__(self, name, value):
		'''
		Overwrite variable assignment in a way, that not only the value of
		is set, but also a update message to the sensor server is send. 
		Thus, whenever using 'valueHolder.var = value' is called, a
		'sensor-update "var" value' is sent to the server. 

		@param	name	name of variable to assign a value
		@param	value	value to be assigned
		'''
		self.set(name, value)

	def set(self, name, value, updateRemote = True):
		'''
		Set value of a named variable, decide if update message is sent or not.

		@param	name			name of variable to assign a value
		@param	value			value to be assigned
		@param	updateRemote	if True, send update message
		'''
		self.__setInternal(name, value)

		if updateRemote:
			self.sensorClient.sendMsg('sensor-update', varName=name, varValue=value)
		
	def get(self, name):
		'''
		Get value assigned to a named variable.

		Throws an exception if variable does not exist (because nothing was assigned to it yet).

		@param	nam		name of variable to get the value
		@return			currently assigned variable value		
		'''
		return self.__dict__[name] 

class RemoteSensor(threading.Thread):
	'''
	Implementation of the Scratch Remote Sensor protocol.
	'''

	__sock 			= None	# TCP socket to communicate to server
	__stopRcvThread = None	# Controll flag for receiver thread 
	__host			= None	# Sensor server host
	__port			= None	# Sensor server port

	values 			= None	# holds an instance of @SensorValues

	updateHandler  = None	# Call back handler for sensor updates
	messageHandler = None	# Call back handler for message updates

	def __init__(self, host = DEFAULT_HOST, port = DEFAULT_PORT):
		'''
		Construct new remote sensor connected to given server on given port.
		If server is not reachable, an exception is thrown.

		@param	host	IP/hostname of Scratch sensor server
		@param	port	port of Scratch sensor server
		'''

		self.__host = host
		self.__port = port
	
		threading.Thread.__init__(self)
		self.daemon = True

		self.values = SensorValues(self)

	def connect(self, tryHard = False):

		logging.info("Connecting to Scratch at %s:%d" % (self.__host, self.__port))

		if tryHard:

			while True:
				try:
					RemoteSensor.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					RemoteSensor.__sock.connect((self.__host, self.__port))
					break
				except socket.error:
					logging.info("Connect failed. Retrying in 2 sec.!")
					try:
						time.sleep(2)
					except KeyboardInterrupt:
						exit(0)
				except KeyboardInterrupt:
					exit(0)

		else:
			RemoteSensor.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			RemoteSensor.__sock.connect((self.__host, self.__port))

		logging.info("Successfully connected!")

	def shutdown(self):
	
		if self.__stopRcvThread == None:
			return

		logging.info("Shutting down connection to Scratch")

		self.__stopRcvThread = True 

		try:
			self.__sock.shutdown()
			self.__sock.close()
		except:
			pass

	def __del__(self):
		'''
		Destructor for remote sensor
		'''

		try:
			RemoteSensor.__sock.close()
		except:
			pass

	def sendMsg(self, msgType, message = None, varName=None, varValue=None, **msgParam):
		'''
		Send generic message to sensor server. 

		@param	msgType		message type ('sensor-update' or 'broadcast')
		@param	message		if msgType is 'broadcast' this holds the massage to send
		@param	varName		if msgType is 'sensor-update', and only one variable should be
							broadcasted, this holds the variable name
		@param	varVale		if msgType is 'sensor-update', and only one variable should be
							broadcasted, this holds the variable vale 
		@param	**msgParam	if msgType is 'sensor-update', and many variables should be
							broadcasted, they could be specified here as key-value pairs
							(e.g. x=1, y=2, ...) 
		'''

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

		logging.info("Sending message: %s" % msg)

		RemoteSensor.__sock.sendall(struct.pack('!I', len(msg)))
		RemoteSensor.__sock.sendall(msg)

	def recvMsg(self):
		'''
		Wait (blocking) for an incoming message. This method is used within the receiver thread.

		@return	received message (raw)
		'''

		msg = RemoteSensor.__sock.recv(4)

		if not msg:
			return None

		(l, ) = struct.unpack('!I', msg)
				
		msg = RemoteSensor.__sock.recv(l)

		if not msg:
			return None

		return msg 

	def parseMsg(self, msg):
			'''
			Parse a message received from the server. For messages of type 'sensor-update' the
			value of the corresponding variable int the value holder instance is set. If a 
			callback handler (updateHandler) is assigned, this handler is called. 

			For messages of type 'broadcast', the callback handler (messageHandler) is called
			if assigned.

			@param	msg		raw message as received from server
			'''
	
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
		'''
		Broadcast a message to the server.

		@param	msg		message to broadcast
		'''

		self.sendMsg('broadcast', msg)

	def run(self):
		'''
		Run method called when thread is started.
		'''

		self.__stopRcvThread = False


		while not self.__stopRcvThread:

			try:
				msg = self.recvMsg()
		
				if not msg:
					time.sleep(0.1)	
				else:
					self.parseMsg(msg)

			except:
				pass

		self.__stopRcvThread = None 

