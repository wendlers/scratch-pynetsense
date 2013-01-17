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
import RPi.GPIO as GPIO

from scratch.remotesensor import RemoteSensor 

rs = None

def setupPins():

	GPIO.setmode(GPIO.BCM)

	for pin in [ 4, 17, 18, 21, 22, 23, 24, 25 ]:

		GPIO.setup(pin, GPIO.OUT)	
		GPIO.output(pin, GPIO.LOW)
		rs.values.set("DIO%d" % pin, 0)
		rs.values.set("IO%d" % pin, 0)
			
def updateHandler(var, val):
	'''
	Handler called for incoming sensor-updates ...
	'''

	vu  = var.upper()

	if isinstance(val, (int)):
		
		if vu in ["DIO4", "DIO17", "DIO18", "DIO21", "DIO22", "DIO23", "DIO24", "DIO25" ]:

			pin = int(var[3:])

			if val == 0:
				GPIO.setup(pin, GPIO.OUT)	
			elif val == 1:
				GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)	
			else:
				logging.warn("Unknown direction %s for pin %s" % (pin, vu))

		elif vu in ["IO4", "IO17", "IO18", "IO21", "IO22", "IO23", "IO24", "IO25" ]:

			pin = int(var[2:])

			if val == 0:
				GPIO.output(pin, GPIO.LOW)
			elif val == 1:
				GPIO.output(pin, GPIO.HIGH)
			else:
				logging.warn("Unknown setting%s for pin %s" % (pin, vu))

	else:
		logging.warn("Allowed value for %s is 0 or 1 (was %s)" % (val, vu))


def messageHandler(t, msg):
	'''
	Handler called for incoming broadcast messages ... 
	'''
	pass

try:
	# Configure logging for RemoteSensor to show DEBUG messages ...
	logging.basicConfig(
		level=logging.DEBUG,
		format='%(asctime)s %(levelname)-8s %(message)s',
		datefmt='%m-%d %H:%M',
	)

	# Remote sensor connected to default host/port (localhost:42001)
	rs = RemoteSensor()

	# Register callback handler for sensor-updates
	rs.updateHandler  = updateHandler

	# Register callback handler for broadcast messages
	rs.messageHandler = messageHandler
	
	# Start receiver thread
	rs.start()
	
	setupPins()

	raw_input('Press Enter to quit...\n')
	
except Exception as e:
	print(e)

finally:
	GPIO.cleanup()
