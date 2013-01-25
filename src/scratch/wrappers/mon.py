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

import time
import socket
import logging

from scratch.remotesensor import RemoteSensor, DEFAULT_HOST, DEFAULT_PORT 

class MonitoringRemoteSensor(RemoteSensor):

	__args = None 

	def __init__(self, args = {}):

		logging.info("MonitoringRemoteSensor initialized")
		logging.debug("Wrapper arguments: %s" % args)

		self.__args = args

		host = DEFAULT_HOST

		if self.__args.has_key('host'):
			host = self.__args['host']

		port = DEFAULT_PORT

		if self.__args.has_key('port'):
			try:
				port = int(self.__args['port'])
			except:
				logging.warn("Invalid port [%s] ignored" % self.__args['port'])

		RemoteSensor.__init__(self, host, port)

		self.updateHandler  = self.__updateHandler
		self.messageHandler = self.__messageHandler

	def __updateHandler(self, var, val):
		'''
		Handler called for incoming sensor-updates ...
		'''
		logging.info("Received update: %s = %s" % (var, val))

	def __messageHandler(self, t, msg):
		'''
		Handler called for incoming broadcast messages ... 
		'''
		logging.info("Received message: %s" % msg)

	def serveForever(self):

		logging.info("MonitoringRemoteSensor entering server loop")

		hbCounterMax = 50
		hbCounter 	 = 0

		try:

			self.connect(True)
			self.start()

			while True:

				try:
					time.sleep(0.1)

					hbCounter = hbCounter + 1

					if hbCounter == hbCounterMax:
						hbCounter = 0
						self.bcastMsg('heartbeat-mon')

				except socket.error as e:
					logging.warn("Lost connection to Scratch server!")
					self.connect(True)

				except KeyboardInterrupt:
					break
			
		except Exception as e:
			logging.error(e)

