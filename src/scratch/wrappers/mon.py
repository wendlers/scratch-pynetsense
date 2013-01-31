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
	'''
	This remote sonsor just listens for sensor updates and messages to 
	print them to the log. 

	This remote sensor broadcasts a "heartbeat-mon" message every 5sec. to show it is
	still alive. This is mainly used internally to get aware of connection loss and to initiate 
	a reconnect. 
	'''

	__args = None 

	# sensor name e.g. to use in heart-beat
	name = "mon"

	def __init__(self, myArgs = {}):
		'''
		Create a new instance of the monitoring remote sensor. 

		@param	myArgs	arguments for the sensor: host and port.
		'''

		RemoteSensor.__init__(self, args = myArgs)

		self.updateHandler  = self.__updateHandler
		self.messageHandler = self.__messageHandler

	def __updateHandler(self, var, val):
		'''
		Handler called for incoming sensor-updates ...

		@param	var		name of variable which was updated
		@param	val		new value assigned to var
		'''

		logging.info("Received update: %s = %s" % (var, val))

	def __messageHandler(self, t, msg):
		'''
		Handler called for incoming broadcast messages ... 

		@param	t		message type (currently always broadcast)
		@param	msg		message received
		'''

		logging.info("Received message: %s" % msg)

	def worker(self):
		'''
		The remote seonsor worker.
		'''
		pass
