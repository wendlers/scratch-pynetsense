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
import time
import socket
import RPi.GPIO as GPIO

from scratch.remotesensor import RemoteSensor, DEFAULT_HOST, DEFAULT_PORT 

class PiRemoteSensor(RemoteSensor):

	__args = None 

	__inputs = []

	def __init__(self, args = {}):

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

		self.updateHandler = self.__updateHandler

	def __setupPins(self):

		GPIO.setmode(GPIO.BCM)

		self.__inputs = []

		for pin in [ 4, 17, 18, 21, 22, 23, 24, 25 ]:

			GPIO.setup(pin, GPIO.OUT)	
			GPIO.output(pin, GPIO.LOW)
			self.values.set("DIO%d" % pin, 0)
			self.values.set("IO%d" % pin, 0)
				
	def __inputMonitor(self):

		changed = False

		for pin in self.__inputs:

			i = GPIO.input(pin)

			if i != self.values.get("IO%d" % pin):
				self.values.set("IO%d" % pin, i)
				changed = True

		if changed:
			self.bcastMsg("input-changed")

	def __updateHandler(self, var, val):
		'''
		Handler called for incoming sensor-updates ...
		'''
		vu  = var.upper()

		if isinstance(val, (int)):
			
			if vu in ["DIO4", "DIO17", "DIO18", "DIO21", "DIO22", "DIO23", "DIO24", "DIO25" ]:

				pin = int(var[3:])

				if val == 0:
					logging.debug("Setting %s as OUTPUT" % vu)
					GPIO.setup(pin, GPIO.OUT)	
					slef.__inputs[:] = (value for value in self.__inputs if value != pin)
					logging.debug("Currently monitored inputs: %s" % self.__inputs)
				elif val == 1:
					logging.debug("Setting %s as INPUT" % vu)
					GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)	
					self.__inputs.append(pin)
					logging.debug("Currently monitored inputs: %s" % self.__inputs)
				else:
					logging.warn("Unknown direction %d for pin %s" % (val, vu))

			elif vu in ["IO4", "IO17", "IO18", "IO21", "IO22", "IO23", "IO24", "IO25" ]:

				pin = int(var[2:])

				if val == 0:
					GPIO.output(pin, GPIO.LOW)
				elif val == 1:
					GPIO.output(pin, GPIO.HIGH)
				else:
					logging.warn("Unknown setting %d for pin %s" % (val, vu))

		else:
			logging.warn("Allowed value for %s is only 0 or 1 (was %s)" % (val, vu))

	def serveForever(self):

		logging.info("PiRemoteSensor entering server loop")

		hbCounterMax = 50
		hbCounter 	 = 0

		try:

			self.connect(True)
			self.__setupPins()
			self.start()

			while True:

				try:
					self.__inputMonitor()
					time.sleep(0.1)

					hbCounter = hbCounter + 1

					if hbCounter == hbCounterMax:
						hbCounter = 0
						self.bcastMsg('heartbeat-pi')

				except socket.error as e:
					logging.warn("Lost connection to Scratch server!")
					self.connect(True)

				except KeyboardInterrupt:
					break
			
		except Exception as e:
			logging.error(e)

		finally:
			GPIO.cleanup()

