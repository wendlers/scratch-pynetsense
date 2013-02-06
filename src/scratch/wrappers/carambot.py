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

import logging

from ubot.rob.carambot import Robot
from scratch.remotesensor import RemoteSensor, DEFAULT_HOST, DEFAULT_PORT 

class DummyVehicle:

	def fw(self, count):
		logging.debug("DummyVehicle: fw(%d)" % count)
		return True
	
	def br(self):
		logging.debug("DummyVehicle: br")

	def tr(self, deg):
		logging.debug("DummyVehicle: tr for %d deg." % deg)

	
class DummyPanRf:

	def rangeAt(self, deg):
		logging.debug("DummyVehicle: rangeAt for %d deg." % deg)
		return deg + 1

class DummyBot:

	def __init__(self, sherpaPort, advaced = False):

		self.vehicle = DummyVehicle()
		self.panrf	 = DummyPanRf()

		logging.debug("Starting dummy bot with sherpaPort %s" % sherpaPort)
	
class CarambotRemoteSensor(RemoteSensor):
	'''
	TODO
	'''

	# carambot robot instance
	robot = None

	# sensor name e.g. to use in heart-beat
	name = "carambot"

	def __init__(self, myArgs = {}):
		'''
		Create a new instance of the carambot remote sensor. 

		@param	myArgs	arguments for the sensor: host, port, sherpaPort.
		'''

		sherpaPort = '/dev/ttyUSB0'

		if myArgs.has_key('sherpaPort'):
			sherpaPort = myArgs['sherpaPort']

		dummyBot = False
	
		if myArgs.has_key('dummyBot') and myArgs['dummyBot'].lower() == 'true':
			dummyBot = True

		if dummyBot:
			self.robot = DummyBot(sherpaPort, True)
		else:
			self.robot = Robot(sherpaPort, True)
 
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

		if msg == "forward": 

			full = self.robot.vehicle.fw(self.values.moveticks)
			if not full:
				self.bcastMsg('obstacle-detected')

		elif msg == "stop": 

			self.robot.vehicle.br()

		elif msg == "turn": 

			self.robot.vehicle.tr(self.values.turndeg)

		elif msg == "range": 

			self.values.range = self.robot.panrf.rangeAt(self.values.rangedeg)
			self.bcastMsg('range-updated')

		else:

			logging.warn("Unknown message: %s" % msg)	

	def setupVariables(self):

		self.values.forwardticks 	= 0
		self.values.turndeg 		= 0
		self.values.rangedeg 		= 0
		self.values.range	 		= 0

	def worker(self):
		'''
		The remote seonsor worker.
		'''
		pass
