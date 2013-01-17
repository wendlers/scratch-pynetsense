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

from scratch.remotesensor import RemoteSensor 

def updateHandler(var, val):
	'''
	Handler called for incoming sensor-updates ...
	'''
	print("-> received update: %s = %s" % (var, val))

def messageHandler(t, msg):
	'''
	Handler called for incoming broadcast messages ... 
	'''
	print("-> received message: %s" % msg)

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
	
	raw_input('Press Enter to quit...\n')
	
except Exception as e:
	print(e)
