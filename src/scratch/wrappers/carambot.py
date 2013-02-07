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

from ubot.rob.carambot 		import Robot
from ubot.rob.simplepilot 	import RobotPilot

from scratch.remotesensor import RemoteSensor, DEFAULT_HOST, DEFAULT_PORT 

class DummyVehicle:
	'''
	Dummy vehicle implementation for testing.
	'''
	
	def fw(self, count = 0):
		logging.debug("DummyVehicle: fw(%d)" % count)
		return True
	
	def br(self):
		logging.debug("DummyVehicle: br")

	def tr(self, deg):
		logging.debug("DummyVehicle: tr for %d deg." % deg)

class DummyRf:
	'''
	Dummy range-finder implementation for testing.
	'''

	minRange = None

	def __init__(self):
		self.minRange = 5 

	def currentRange(self):
		return 15
	
class DummyPanRf:
	'''
	Dummy pan based range-finder implementation for testing.
	'''

	rf = None

	def __init__(self):
		self.rf = DummyRf() 

	def rangeAt(self, deg):
		logging.debug("DummyVehicle: rangeAt for %d deg." % deg)
		return deg + 1

	def scanArea(self, positions = [ 0, 45, 90, 135, 180] , endPos = 90):

		return [ { 0 : 22} , {45 : 10}, {90 : 8}, {135 : 50}, {180: 7} ] 

class DummyBot:
	'''
	Dummy robot implementation for testing.
	'''

	def __init__(self, sherpaPort, advanced = False):

		self.advanced 	= advanced
		self.vehicle 	= DummyVehicle()
		self.panrf	 	= DummyPanRf()

		logging.debug("Starting dummy bot with sherpaPort %s" % sherpaPort)
	
class CarambotRemoteSensor(RemoteSensor):
	'''
	Remote seonsor implementation to control carambot. 

	Messages:
	
		forward				move robot forward for "forwardticks"
		stop				stop robot
		turn				turn robot for "turndeg" (-90..90)
		range				range scan at "rangedeg" (-90..90)
		rangeminmax			area range scan to determine min/max range
							min. range/pos returned in "rangemin" and "rangemindeg"
							max. range/pos returned in "rangemax" and "rangemaxdeg"

	Variables:

		forwardticks[out]	ticks to move on message "forward"
		turndeg[out]		deg. to turn on "turn" (-90..90)
		rangedeg[out]		deg. at which to perform scan on "range" (-90..90)
		range[out]			renage (in cm) measured at "rangedeg"
		rangemin[out]		min. range (in cm) found at "rangeminmax"
		rangemax[out]		man. range (in cm) found at "rangeminmax"
		rangemindeg[out]	deg. at which min. range was found at "rangeminmax"
		rangemaxdeg[out]	deg. at which max. range was found at "rangeminmax"
		autopilot[in]		set to 1 to enable autopilot, 0 to disable
							if set to 1, no messages are accepted by robot

	'''

	# carambot robot instance
	robot = None

	# autopilot
	pilot = None

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

		if var == "autopilot":
			if val == 1:

				logging.debug("Starting autupilot thread")
				self.pilot = RobotPilot(self.robot)
				self.pilot.daemon = True
				self.pilot.start()
				self.bcastMsg('autopilot-started')

			else:

				if not self.pilot == None:

					logging.debug("Autopilot is running, trying to stop it ...")
					self.pilot.abort = True
					self.pilot.join()
					del self.pilot
					self.bcastMsg('autopilot-stoped')

	def __messageHandler(self, t, msg):
		'''
		Handler called for incoming broadcast messages ... 

		@param	t		message type (currently always broadcast)
		@param	msg		message received
		'''

		logging.info("Received message: %s" % msg)

		if not self.pilot == None:
			logging.warn("Not processing commands: autopilot is active")
			self.bcastMsg('autopilot-active')
			return

		if msg == "forward": 

			ticks = 100
		
			if self.values.forwardticks > 0:
				ticks = self.values.forwardticks

			full = self.robot.vehicle.fw(ticks)

			if not full:
				self.bcastMsg('obstacle-detected')
			else:
				self.bcastMsg('stoped')

		elif msg == "stop": 

			self.robot.vehicle.br()
			self.bcastMsg('stoped')

		elif msg == "turn": 

			self.robot.vehicle.tr(self.values.turndeg)
			self.bcastMsg('stoped')

		elif msg == "range": 

			self.values.range = self.robot.panrf.rangeAt(self.values.rangedeg)
			self.bcastMsg('range-updated')

		elif msg == "rangeminmax": 

			area = self.robot.panrf.scanArea()
		
			min 	= 9999 
			max 	= 0 
			mindeg 	= 0  
			maxdeg 	= 0 

			for v in area:
				for p in v:
					
					if v[p] > max:
						max = v[p] 
						maxdeg = p

					if v[p] < min:
						min = v[p] 
						mindeg = p

			self.values.rangemin 	= min
			self.values.rangemindeg = mindeg
			self.values.rangemax 	= max
			self.values.rangemaxdeg = maxdeg
	
			self.bcastMsg('rangeminmax-updated')

		else:

			logging.warn("Unknown message: %s" % msg)	

	def setupVariables(self):

		self.values.forwardticks 	=  0
		self.values.turndeg 		=  0
		self.values.rangedeg 		=  0
		self.values.range	 		= -1
		self.values.rangemin 		= -1 
		self.values.rangemax 		= -1 
		self.values.rangemindeg		= -1 
		self.values.rangemaxdeg 	= -1 
		self.values.autopilot		=  0

	def worker(self):
		'''
		The remote seonsor worker.
		'''
		pass
