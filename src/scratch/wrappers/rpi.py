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
	'''
	This remote sonsor allows to control the build in GPIOs of a Raspberry Pi.

	It offers the following variables for setting the direction of an GPIO:

	* DIO4, DIO17, DIO18, DIO21, DIO22, DIO23, DIO24, DIO25

	Assigning 0 to a DIOx variable configures the port as an output. By assigning 1
	the port will be configured to be in input with internal pull-down enabled. 

	E.g. to make IO port 24 an input and 25 an output, send the following message:

		sensor-update "DIO24" 1	"DIO25" 0

	* Note: by default, all ports are configured as inputs. 
	* Hint: to configure the direction of an port from Scratch, create a global varaibale
	  named like the port (e.g. DIO24), and then assigne a value to it (e.g. 1). 	

	To set/get the current value (high/low) of an port, use one of this variables:

	* IO4, IO17, IO18, IO21, IO22, IO23, IO24, IO25

	If a port is configured as an output, assigning 1 will set it to high, and
	asisigning 0 will set it to low. 

	If a port is configured as an input, the remote sensor will constantly monitor
	this port for state change. Every time a state change is detected, a sensor-update
	message is sent. E.g. if port 24 is configured as input, and its state changes from
	low to high, the following is sent to the server:

		sensor-update "IO24" 1

	Additionally the message "input-changed is broadcasted to the server is a state change
	for at least one of the input ports was detected. 

	* Hint: to read the value from scratch, insert the sensor value block and select the 
	  coresponding port varaible (e.g. IO24).

	* Hint: to check in scratch for changed input ports, listen to the message "input-changed", 
	  and at the moment the message was received, check if the port of interest changed. This is
	  much more efficent then polling a port variable directely in a loop.

	Additonally, this remote sensor broadcasts a "heartbeat-pi" message every 5sec. to show it is
	still alive. This is mainly used internally to get aware of connection loss and to initiate 
	a reconnect. 
	'''

	__args 		= None 
	__inputs 	= []

	# sensor name e.g. to use in heart-beat
	name = "pi"

	def __init__(self, args = {}):
		'''
		Create a new instance of the monitoring remote sensor. 

		@param	args	arguments for the sensor: host and port.
		'''

		RemoteSensor.__init__(self, args)

		self.updateHandler = self.__updateHandler

	def __del__(self):
		'''	
		Release GPIOs
		'''

		try:
			GPIO.cleanup()
		except:
			pass

	def __setupPins(self):
		'''
		Initially setup the pins (all OUTPUT). This also sends the sensor-update
		message to the server to anounce in which state the pins are. 
		'''
		
		GPIO.setmode(GPIO.BCM)

		self.__inputs = []

		for pin in [ 4, 17, 18, 21, 22, 23, 24, 25 ]:

			GPIO.setup(pin, GPIO.OUT)	
			GPIO.output(pin, GPIO.LOW)
			self.values.set("DIO%d" % pin, 0)
			self.values.set("IO%d" % pin, 0)
				
	def __updateHandler(self, var, val):
		'''
		Handler called for incoming sensor-updates ...

		@param	var		name of variable which was updated
		@param	val		new value assigned to var
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

	def worker(self):
		'''
		Check all ports which are configured as input for state change. If a 
		state change was detected report the change through a sensor-update message.
		Also a "input-changed" message is broadcasted.
		'''
	
		changed = False

		for pin in self.__inputs:

			i = GPIO.input(pin)

			if i != self.values.get("IO%d" % pin):
				self.values.set("IO%d" % pin, i)
				changed = True

		if changed:
			self.bcastMsg("input-changed")

